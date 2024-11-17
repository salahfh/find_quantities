import itertools
from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products, extract_calculation_report
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.model import Inventory
from find_quantity.solver import Solver, ShowRoom
from find_quantity.report import Report
from find_quantity.validation_data import ValidationShowroomData

DataLoader = ''

PROJECT_FOLDER = Path(r'data/')
RAW_PRODUCTS_DATA: Path = Path(r'data\produits.csv')
RAW_SHOWROOMS_DATA: Path = Path(r'data\showrooms.csv')
STEP_ONE_TRANSFORM_PATH = PROJECT_FOLDER / 'output' / '1. transform'
STEP_TWO_CALCULATE_PATH = PROJECT_FOLDER / 'output' / '2. Calculate'
STEP_THREE_VALIDATE_PATH = PROJECT_FOLDER / 'output' / '3. Validate'
SOLVER_ERROR_TOLERANCE = [1 / 10**i for i in [9, 6, 3]]
SOLVER_PRODUCT_MAX_PERCENTAGE = [.1, .12, .15, .2, .3, .5, .7]


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
            path=self.input_folder / f'products_transformed.csv')
        s_list_all = extract_showrooms(
            path=self.input_folder / f'showrooms_transformed.csv')

        for month, p_list, s_list in zip(p_list_all.keys(), p_list_all.values(), s_list_all.values()):
            products = ProductTransformer(products=p_list).load()
            inv = Inventory(products=products)
            showrooms_solved: list[ShowRoom] = []

            for tolerence, max_product_percentage in itertools.product(SOLVER_ERROR_TOLERANCE, SOLVER_PRODUCT_MAX_PERCENTAGE):
                print(f'\t{
                      month}/Params - tolerence: {tolerence}, product_percen: {max_product_percentage}')
                if not inv.has_products():
                    print(f'Month {month}: Inventory empty.')
                    break

                showrooms = ShowroomTransformer(showrooms=s_list).load()
                for sh in showrooms:
                    if sh in showrooms_solved:
                        continue
                    solver = Solver(
                        tolerance=tolerence, max_product_sales_percentage=max_product_percentage)
                    solver.add_products(products=inv.get_products())
                    solver.add_showroom(sh)
                    solver.calculate_quantities()
                    if solver.is_it_solved_correctly():
                        inv.update_quantities(sales=sh.sales)
                        sh.sales = inv.split_products(sales=sh.sales)
                        report.write_showrooms_report(month=month, showroom=sh)
                        report.write_metrics(
                            month=month, metrics=solver.metrics)
                        showrooms_solved.append(sh)
                    else:
                        print(f'{sh.refrence}: Cannot find optimal solution')


class ValidateQuantitiesCommand:
    def __init__(self):
        pass

    def excute(self):
        raw_products = extract_products(RAW_PRODUCTS_DATA)
        raw_showrooms = extract_showrooms(RAW_PRODUCTS_DATA)
        calculation_report = extract_calculation_report(
            path=STEP_TWO_CALCULATE_PATH / 'showrooms_calculation_report.csv'
        )
        for month, showrooms in calculation_report.items():
            for sh in showrooms.values():
                vd = ValidationShowroomData(
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
