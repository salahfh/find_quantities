from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products, extract_calculation_report
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.model import Inventory, ShowRoom
from find_quantity.solver import SolverRunner
from find_quantity.report import Report
from find_quantity.validation_data import ValidationShowroomData

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
    def __init__(self):
        self.input_folder = STEP_ONE_TRANSFORM_PATH
        self.output_folder = STEP_TWO_CALCULATE_PATH

    def excute(self):
        report = Report(output_folder=self.output_folder)
        p_list_all = extract_products(
            path=self.input_folder / 'products_transformed.csv')
        s_list_all = extract_showrooms(
            path=self.input_folder / 'showrooms_transformed.csv')

        for month, p_list, s_list in zip(p_list_all.keys(), p_list_all.values(), s_list_all.values()):
            unsolved_showrooms: list[ShowRoom] = list()
            products = ProductTransformer(products=p_list).load()
            showrooms = ShowroomTransformer(showrooms=s_list).load()
            inv = Inventory(products=products)
            sr = SolverRunner(inventory=inv, month=month)
            for sh in showrooms:
                sh_solved, metrics = sr.calc_monthly_quantities(sh=sh)
                if metrics.solved_correctly:
                    report.write_showrooms_report(month=month, showroom=sh_solved)
                    report.write_metrics(month=month, metrics=metrics)
                else:
                    unsolved_showrooms.append(sh)
            for sh in unsolved_showrooms:
                sh_solved, metrics = sr.calc_monthly_quantities(sh=sh)
                if metrics.solved_correctly:
                    report.write_showrooms_report(month=month, showroom=sh_solved)
                    report.write_metrics(month=month, metrics=metrics)

    # collect non optimal solutions
    # filter out those that were solved
    # pick the solution with lowest diff(assigned_sale and calc_sales)
    #   Also the product must be able to cover this solution
    # if found allocate them and recalculate the final amount to make total
    #   monthly sales for all showrooms
    # Run the solver again to find a quantity for the last one


class ValidateQuantitiesCommand:
    def __init__(self):
        pass

    def excute(self):
        # raw_products = extract_products(RAW_PRODUCTS_DATA)
        # raw_showrooms = extract_showrooms(RAW_PRODUCTS_DATA)
        calculation_report = extract_calculation_report(
            path=STEP_TWO_CALCULATE_PATH / 'showrooms_calculation_report.csv'
        )
        for month, showrooms in calculation_report.items():
            for sh in showrooms.values():
                ValidationShowroomData(
                    mois=month,
                    showroom=sh.refrence,
                    difference_in_sales= sh.assigned_total_sales - sh.calculated_total_sales,
                )


class FinalFormatingCommand:
    def __init__(self):
        pass

    def excute(self):
        pass


if __name__ == '__main__':
    # c = ProcessFilesCommand().execute()
    c = CalculateQuantitiesCommand().excute()
    # c = ValidateQuantitiesCommand().excute()
