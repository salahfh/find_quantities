from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products, extract_calculation_report
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.model import Inventory, ShowRoom
from find_quantity.report import Report
from find_quantity.data_quality_control import product_validation, validate_calculated_products, validate_extracted_product_raw_data
from find_quantity.solver import Solver, Metrics


DataLoader = ''

PROJECT_FOLDER = Path(r'data/')
RAW_PRODUCTS_DATA: Path = Path(r'data\produits.csv')
RAW_SHOWROOMS_DATA: Path = Path(r'data\showrooms.csv')
STEP_ONE_TRANSFORM_PATH = PROJECT_FOLDER / 'output' / '1. transform'
STEP_TWO_CALCULATE_PATH = PROJECT_FOLDER / 'output' / '2. Calculate'
STEP_THREE_VALIDATE_PATH = PROJECT_FOLDER / 'output' / '3. Validate'


class SetupFolderStructure:
    pass


class ProcessFilesCommand:
    def __init__(self,
                 product_filepath: Path = Path(r'data\produits.csv'),
                 showrooms_filepath: Path = Path(r'data\showrooms.csv'),
                 ) -> None:
        self.product_filepath = product_filepath
        self.showrooms_filepath = showrooms_filepath
        self.output_folder: Path = STEP_ONE_TRANSFORM_PATH

    def execute(self) -> None:
        report = Report(output_folder=self.output_folder)
        products = extract_products(path=self.product_filepath)
        showrooms = extract_showrooms(path=self.showrooms_filepath)
        for i, (s_list, p_list) in enumerate(zip(showrooms.values(), products.values())):
            month = i+1
            p_transfomer = ProductTransformer(products=p_list)
            p_list = p_transfomer.transform()
            p_merged = p_transfomer.get_merged_products()
            s_list = ShowroomTransformer(showrooms=s_list).transform()
            report.write_product_transformed(month=month,
                                             products=p_list)
            report.write_showroom_transformed(month=month,
                                              showrooms=s_list)
            report.write_merged_products(month=month,
                                         merged_products=p_merged)


class CalculateQuantitiesCommand:
    def __init__(self, cache: dict=None):
        self.input_folder = STEP_ONE_TRANSFORM_PATH
        self.output_folder = STEP_TWO_CALCULATE_PATH

    def execute(self):
        report = Report(output_folder=self.output_folder)
        p_list_all = extract_products(path=self.input_folder / 'products_transformed.csv')
        s_list_all = extract_showrooms(path=self.input_folder / 'showrooms_transformed.csv')
        for month, p_list, s_list in zip(p_list_all.keys(), p_list_all.values(), s_list_all.values()):
            products = ProductTransformer(products=p_list).load()
            showrooms = ShowroomTransformer(showrooms=s_list).load()
            inv = Inventory(products=products)
            solver = Solver()
            
            # Filter showrooms with zero sales
            showrooms = [sh for sh in showrooms if sh.assigned_total_sales]

            # Global showroom
            monthly_showroom = ShowRoom(
                    refrence=f'All_Month_{month}',
                    assigned_total_sales=sum([sh.assigned_total_sales for sh in showrooms])
                )
            print(f'Working on {monthly_showroom}', end='  ')
            monthly_showroom.add_sales(solver.distribute_products_monthly(inventory=inv,
                                                                         target_amount=monthly_showroom.assigned_total_sales))
            report.write_product_transformed(products=inv.get_products(), month=month, filename_prefix='_remaining')

            # Single Showrooms - Recreate new products list
            inv = Inventory(products=[])
            inv.add_products_from_sales(monthly_showroom.sales)
            last_showroom = showrooms[-1]
            for sh in showrooms:
                print('.', end='')
                sh.add_sales(solver.distribute_products_by_showroom(inventory=inv,
                                                    target_amount=sh.assigned_total_sales
                ))
                if sh is last_showroom:
                    sh.add_sales(solver.allocate_remaining_products(inventory=inv))
                report.write_showrooms_report(month=month, showroom=sh)
                report.write_metrics(metrics=Metrics(showroom=sh), month=month)
            print()


class DevideProductTo26Days:
    def execute(self):
        DAYS = 26
        solver = Solver()
        report = Report(output_folder=STEP_THREE_VALIDATE_PATH)
        calculation_report: dict[int, dict[str, ShowRoom]] = extract_calculation_report(
            path=STEP_TWO_CALCULATE_PATH / 'showrooms_calculation_report.csv'
        )
        for month, showrooms in calculation_report.items():
            print(f'Daily Product Distribution {month}', end='\t')
            for sh in showrooms.values():
                print('.', end='')
                inv = Inventory(products=[])
                inv.add_products_from_sales(sh.sales)
                daily_sales = solver.distrubute_remaining_products(inv, DAYS)
                for day, sales in zip(range(1, DAYS+1), daily_sales):
                    sh.add_daily_sales(
                        day=day,
                        sales=sales
                    )
                report.write_daily_sales(month=month, showroom=sh)
            print()
                

class SplitCombinedProductsCommand:
    def execute(self):
        report = Report(output_folder=STEP_THREE_VALIDATE_PATH)
        raw_products = extract_products(RAW_PRODUCTS_DATA)

        calculation_report = extract_calculation_report(
            path=STEP_TWO_CALCULATE_PATH / 'showrooms_calculation_report.csv'
        )
        for month, showrooms, raw_month_products in\
            zip(calculation_report.keys(), calculation_report.values(), raw_products.values()):
            p_transfomer = ProductTransformer(products=raw_month_products)
            p_list = p_transfomer.load()
            for sh in showrooms.values():
                sh.sales = p_transfomer.split_product(sales=sh.sales, all_products=p_list)
                report.write_showrooms_report(month=month, showroom=sh, filename_prefix='_split')


class ValidateQuantitiesCommand:
    def __init__(self):
        pass

    def execute(self):
        report = Report(output_folder=STEP_THREE_VALIDATE_PATH)
        raw_products = extract_products(RAW_PRODUCTS_DATA)
        calculation_report = extract_calculation_report(
            path=STEP_THREE_VALIDATE_PATH / 'showrooms_calculation_report__split.csv'
        )
        validation_data_product_calc = validate_calculated_products(calculation_report)
        simplied_product_raw_data = validate_extracted_product_raw_data(raw_products)
        data = product_validation(validation_data_product_calc, simplied_product_raw_data)
        report.valid_product_quantity_report(data)



class FinalFormatingCommand:
    def __init__(self):
        pass

    def excute(self):
        pass


if __name__ == '__main__':
    # c = SplitCombinedProductsCommand().excute()
    # c = ValidateQuantitiesCommand().excute()
    # c = CalculateQuantitiesCommand().execute()
    c = DevideProductTo26Days().execute()