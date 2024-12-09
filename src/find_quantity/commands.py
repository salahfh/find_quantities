import logging

from find_quantity.configs import config
from find_quantity.extract_csv import (
    extract_calculation_report,
    extract_products,
    extract_showrooms,
)
from find_quantity.model import Inventory, ShowRoom
from find_quantity.read_merge_configs import parse_merge_configs
from find_quantity.report import Report
from find_quantity.solver import Metrics, Solver
from find_quantity.transformer_csv import (
    ProductTransformer,
    ShowroomTransformer,
)

logger = logging.getLogger("find_quantity.cli")


class SetupFolderStructure:
    def execute(self) -> None:
        if config.CLEAN_BEFORE_EACH_RUN:
            config.clean_up()

        config.create_folders()
        report = Report(output_folder=config.PROJECT_FOLDER)
        message = (
            "\nThe {} doesn't exists.\nPlease Replace the template in the folder {}."
        )

        quit_ = False
        if not config.RAW_PRODUCTS_DATA.exists():
            logger.info(message.format(config.RAW_PRODUCTS_DATA, config.PROJECT_FOLDER))
            report.write_product_input_template_file(path=config.RAW_PRODUCTS_DATA)
            quit_ = True

        if not config.RAW_SHOWROOMS_DATA.exists():
            logger.info(
                message.format(config.RAW_SHOWROOMS_DATA, config.PROJECT_FOLDER)
            )
            report.write_showroom_input_template_file(path=config.RAW_SHOWROOMS_DATA)
            quit_ = True

        if not config.MERGE_CONFIG_PATH.exists():
            config.copy_merge_configs()
            logger.info(f"\nThe {config.MERGE_CONFIG_PATH.name} has been created.")

        if quit_:
            exit(0)


class ProcessFilesCommand:
    def execute(self) -> None:
        report = Report(output_folder=config.STEP_ONE_TRANSFORM_PATH)
        products = extract_products(path=config.RAW_PRODUCTS_DATA)
        showrooms = extract_showrooms(path=config.RAW_SHOWROOMS_DATA)
        if len(showrooms) != len(products):
            message = "Number of months mismatch in showroom.csv and produits.csv"
            logger.exception(message)
            raise ValueError(message)
        for month, s_list, p_list in zip(
            showrooms.keys(), showrooms.values(), products.values()
        ):
            p_transfomer = ProductTransformer(products=p_list)
            p_list = p_transfomer.load()
            s_list = ShowroomTransformer(showrooms=s_list).transform()
            report.write_product_transformed(month=month, products=p_list)
            report.write_showroom_transformed(month=month, showrooms=s_list)


class CalculateQuantitiesCommand:
    def execute(self):
        report = Report(output_folder=config.STEP_TWO_CALCULATE_PATH)
        merge_rules = parse_merge_configs(path=config.MERGE_CONFIG_PATH)
        p_list_all = extract_products(
            path=config.STEP_ONE_TRANSFORM_PATH / "products_transformed.csv"
        )
        s_list_all = extract_showrooms(
            path=config.STEP_ONE_TRANSFORM_PATH / "showrooms_transformed.csv"
        )
        for month, p_list, s_list in zip(
            p_list_all.keys(), p_list_all.values(), s_list_all.values()
        ):
            products = ProductTransformer(products=p_list).load()
            showrooms = ShowroomTransformer(showrooms=s_list).load()
            inv = Inventory(products=products, merge_rules=merge_rules)
            solver = Solver()

            # Filter showrooms with zero sales
            showrooms = [sh for sh in showrooms if sh.assigned_total_sales]

            # Global showroom
            monthly_showroom = ShowRoom(
                refrence=f"All_Month_{month}",
                assigned_total_sales=sum([sh.assigned_total_sales for sh in showrooms]),
            )
            logger.info(f"Working on {monthly_showroom}")
            sales = solver.distribute_products_monthly(
                inventory=inv, target_amount=monthly_showroom.assigned_total_sales
            )
            monthly_showroom.add_sales(sales)
            report.write_product_transformed(
                products=inv.get_products(), month=month, filename_prefix="_remaining"
            )

            # # Single Showrooms - Recreate new products list
            inv = Inventory(products=[], merge_rules=merge_rules)
            inv.add_products_from_sales(monthly_showroom.sales)
            last_showroom = showrooms[-1]
            for sh in showrooms:
                sales = solver.distribute_products_by_showroom(
                    inventory=inv, target_amount=sh.assigned_total_sales
                )
                sh.add_sales(sales)
                if sh is last_showroom:
                    sh.add_sales(solver.allocate_remaining_products(inventory=inv))
                report.write_showrooms_report(month=month, showroom=sh)
                report.write_metrics(metrics=Metrics(showroom=sh), month=month)


class DevideProductTo26Days:
    def execute(self):
        solver = Solver()
        report = Report(output_folder=config.STEP_THREE_VALIDATE_PATH)
        merge_rules = parse_merge_configs(path=config.MERGE_CONFIG_PATH)
        calculation_report: dict[int, dict[str, ShowRoom]] = extract_calculation_report(
            path=config.STEP_TWO_CALCULATE_PATH / "showrooms_calculation_report.csv"
        )
        for month, showrooms in calculation_report.items():
            logger.info(f"Daily Product Distribution {month}")
            for i, sh in enumerate(showrooms.values()):
                # Devide to 26 days
                logger.info(f"\t {month}-{i+1:2}: Processing {sh}")
                inv = Inventory(products=[], merge_rules=merge_rules)
                inv.add_products_from_sales(sh.sales)
                daily_sales = solver.distrubute_products_equally(inv, config.DAYS)
                for day, sales in zip(range(1, config.DAYS + 1), daily_sales):
                    sh.add_daily_sales(
                        day=day, month=month, year=config.YEAR, sales=sales
                    )

                # Split by client
                for day in sh.daily_sales:
                    customers = day.total_units_sold
                    inv = Inventory(products=[], merge_rules=merge_rules)
                    inv.add_products_from_sales(day.sales)
                    sales_per_customer = solver.distrubute_products_equally(
                        inv, customers
                    )
                    day.add_customer_sales(sales_per_customer)
                report.write_daily_sales(month=month, showroom=sh)


if __name__ == "__main__":
    # c = GeneratePackagesCommand().execute()
    # c = CalculateQuantitiesCommand().execute()
    c = DevideProductTo26Days().execute()
