from pathlib import Path
import copy

from find_quantity.data_quality_control import (
    product_validation,
    validate_calculated_products,
    validate_extracted_product_raw_data,
)
from find_quantity.extract_csv import (
    extract_calculation_report,
    extract_products,
    extract_showrooms,
    load_merged_products,
    load_raw_file,
)
from find_quantity.model import Inventory, ShowRoom, Product, Sale
from find_quantity.report import Report
from find_quantity.solver import Metrics, Solver
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer, MergeSplitProductsMixin


PROJECT_FOLDER = Path(r"data/")
RAW_PRODUCTS_DATA: Path = Path(r"data\produits.csv")
RAW_SHOWROOMS_DATA: Path = Path(r"data\showrooms.csv")
STEP_ONE_TRANSFORM_PATH = PROJECT_FOLDER / "output" / "1. transform"
STEP_TWO_CALCULATE_PATH = PROJECT_FOLDER / "output" / "2. Calculate"
STEP_THREE_VALIDATE_PATH = PROJECT_FOLDER / "output" / "3. Validate"
DAYS = 26


class SetupFolderStructure:
    pass


class ProcessFilesCommand:
    def execute(self) -> None:
        report = Report(output_folder=STEP_ONE_TRANSFORM_PATH)
        products = extract_products(path=RAW_PRODUCTS_DATA)
        showrooms = extract_showrooms(path=RAW_SHOWROOMS_DATA)
        for i, (s_list, p_list) in enumerate(
            zip(showrooms.values(), products.values())
        ):
            month = i + 1
            p_transfomer = ProductTransformer(products=p_list)
            p_list = p_transfomer.transform()
            p_merged = p_transfomer.get_merged_products()
            s_list = ShowroomTransformer(showrooms=s_list).transform()
            report.write_product_transformed(month=month, products=p_list)
            report.write_showroom_transformed(month=month, showrooms=s_list)
            report.write_merged_products(month=month, merged_products=p_merged)


class CalculateQuantitiesCommand:
    def execute(self):
        report = Report(output_folder=STEP_TWO_CALCULATE_PATH)
        p_list_all = extract_products(path=
            STEP_ONE_TRANSFORM_PATH / "products_transformed.csv"
        )
        s_list_all = extract_showrooms(path=
            STEP_ONE_TRANSFORM_PATH / "showrooms_transformed.csv"
        )
        for month, p_list, s_list in zip(
            p_list_all.keys(), p_list_all.values(), s_list_all.values()
        ):
            products = ProductTransformer(products=p_list).load()
            showrooms = ShowroomTransformer(showrooms=s_list).load()
            inv = Inventory(products=products)
            solver = Solver()

            # Filter showrooms with zero sales
            showrooms = [sh for sh in showrooms if sh.assigned_total_sales]

            # Global showroom
            monthly_showroom = ShowRoom(
                refrence=f"All_Month_{month}",
                assigned_total_sales=sum([sh.assigned_total_sales for sh in showrooms]),
            )
            print(f"Working on {monthly_showroom}", end="  ")
            sales = solver.distribute_products_monthly(
                inventory=inv, target_amount=monthly_showroom.assigned_total_sales
            )
            monthly_showroom.add_sales(sales)
            report.write_product_transformed(
                products=inv.get_products(), month=month, filename_prefix="_remaining"
            )

            # Single Showrooms - Recreate new products list
            inv = Inventory(products=[])
            inv.add_products_from_sales(monthly_showroom.sales)
            last_showroom = showrooms[-1]
            for sh in showrooms:
                print(".", end="")
                sales = solver.distribute_products_by_showroom(
                    inventory=inv, target_amount=sh.assigned_total_sales
                )
                sh.add_sales(sales)
                if sh is last_showroom:
                    sh.add_sales(solver.allocate_remaining_products(inventory=inv))
                report.write_showrooms_report(month=month, showroom=sh)
                report.write_metrics(metrics=Metrics(showroom=sh), month=month)
            print()


class DevideProductTo26Days:
    def execute(self):
        solver = Solver()
        report = Report(output_folder=STEP_THREE_VALIDATE_PATH)
        calculation_report: dict[int, dict[str, ShowRoom]] = extract_calculation_report(
            path=STEP_TWO_CALCULATE_PATH / "showrooms_calculation_report.csv"
        )
        for month, showrooms in calculation_report.items():
            print(f"Daily Product Distribution {month}", end="\t")
            for sh in showrooms.values():
                # Devide to 26 days
                print(".", end="")
                inv = Inventory(products=[])
                inv.add_products_from_sales(sh.sales)
                daily_sales = solver.distrubute_products_equally(inv, DAYS)
                for day, sales in zip(range(1, DAYS + 1), daily_sales):
                    sh.add_daily_sales(day=day, sales=sales)

                # Split by client 
                for day in sh.daily_sales:
                    customers = day.total_units_sold
                    inv = Inventory(products=[])
                    inv.add_products_from_sales(day.sales)
                    sales_per_customer = solver.distrubute_products_equally(inv, customers)
                    day.add_customer_sales(sales_per_customer)
                report.write_daily_sales(month=month, showroom=sh)
            print()
            break



class SplitCombinedProductsCommand:
    def execute(self):
        report = Report(output_folder=STEP_THREE_VALIDATE_PATH)
        merged_products = load_merged_products(path=STEP_ONE_TRANSFORM_PATH / 'merged_product.csv')
        final_report = load_raw_file(path=STEP_THREE_VALIDATE_PATH / 'daily_sales.csv')
        p_transfomer = MergeSplitProductsMixin(products=[])
        data = []
        for line in final_report:
            # Handle returned products
            if float(line['prix']) < 0:
                line['prix'] = float(line['prix']) * -1
                line['Units_sold'] = float(line['Units_sold']) * -1
            stem = p_transfomer._find_product_stem(line['n_article'], prefix=['-C'])
            if stem:
            # Split Merged Products
                pc = Product(
                    n_article=line['n_article'],
                    designation=line['designation'],
                    groupe_code=line['groupe_code'],
                    prix=float(line['prix']),
                    stock_qt=int(line['Units_sold']),
                    tee=float(line['TEE']),
                    rta=float(line['RTA']),
                )
                code = (line['mois'], stem)
                for i in [1, 2]: 
                    p = copy.copy(pc)
                    line = copy.copy(line)
                    p.n_article = merged_products[code][f'p{i}_n_article']
                    p.designation = merged_products[code][f'p{i}_designation']
                    p.prix = float(merged_products[code][f'p{i}_prix'])
                    sale = Sale(product=p, units_sold=p.stock_qt)

                    line['n_article'] = p.n_article
                    line['designation'] = p.designation
                    line['prix'] = p.prix
                    line['Total'] = sale.sale_total_amount
                    line['Total TTC'] = sale.total_ttc
                    data.append(line)
                continue
            data.append(line)
        report.write_generic_list_of_dicts(ld=data, filename='final_daily_sales')


class ValidateQuantitiesCommand:
    def execute(self):
        report = Report(output_folder=STEP_THREE_VALIDATE_PATH)
        raw_products = extract_products(path=RAW_PRODUCTS_DATA)
        calculation_report = extract_calculation_report(
            path=STEP_THREE_VALIDATE_PATH / "showrooms_calculation_report__split.csv"
        )
        validation_data_product_calc = validate_calculated_products(calculation_report)
        simplied_product_raw_data = validate_extracted_product_raw_data(raw_products)
        data = product_validation(
            validation_data_product_calc, simplied_product_raw_data
        )
        report.valid_product_quantity_report(data)


class FinalFormatingCommand:
    def __init__(self):
        pass

    def excute(self):
        pass


if __name__ == "__main__":
    c = SplitCombinedProductsCommand().execute()
