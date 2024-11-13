from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.solver import Solver
from find_quantity.report import Report

DataLoader = ''

PROJECT_FOLDER = Path(r'data/')
STEP_ONE_TRANSFORM_PATH = PROJECT_FOLDER / 'output' / '1. transform'
STEP_TWO_TRANSFORM_PATH = PROJECT_FOLDER / 'output' / '2. Calculate'


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
        products = extract_products(filepath=self.product_filepath)
        showrooms = extract_showrooms(filepath=self.showrooms_filepath)
        for i, (s_list, p_list) in enumerate(zip(showrooms.values(), products.values())):
            month = i+1
            p_list = ProductTransformer(products=p_list).transform()
            s_list = ShowroomTransformer(showrooms=s_list).transform()
            report.write_product_obj(filename=f'products_transformed_{month}.csv',
                                     products=p_list)
            report.write_showroom_obj(filename=f'showrooms_transformed_{month}.csv',
                                     showrooms=s_list)

            

class CalculateQuantitiesCommand:
    def __init__(self):
        self.input_folder = STEP_ONE_TRANSFORM_PATH
        self.output_folder = STEP_TWO_TRANSFORM_PATH
    
    def excute(self):
        report = Report(output_folder=self.output_folder)
        # TODO: Rewrite this part and remove the coupling between data and file (mois column?)
        p_list = extract_products(filepath=self.input_folder / 'products_transformed_1.csv')['mois']
        s_list = extract_showrooms(filepath=self.input_folder / 'showrooms_transformed_1.csv')['mois']
        products = ProductTransformer(products=p_list).load()
        showrooms = ShowroomTransformer(showrooms=s_list).load()
        # solver = Solver(products=products, showrooms=showrooms).calculate_quantities()
        for s in showrooms:
            # print(type(p.stock_qt))
            print(s)



class ValidateQuantitiesCommand:
    def __init__(self):
        pass

    def excute(self):
        pass


class FinalFormatingCommand:
    def __init__(self):
        pass

    def excute(self):
        pass





if __name__ == '__main__':
    # c = ProcessFilesCommand().execute()
    c = CalculateQuantitiesCommand().excute()