from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.report import Report

PROJECT_FOLDER = Path(r'data/')


class SetupFolderStructure:
    pass


class ProcessFilesCommand:
    def __init__(self,
                 product_filepath: Path = Path(r'data\produits.csv'),
                 showrooms_filepath: Path = Path(r'data\showrooms.csv'),
                 ) -> None:
        self.product_filepath = product_filepath
        self.showrooms_filepath = showrooms_filepath
        self.output_folder: Path = PROJECT_FOLDER / 'output' / '1. transform'
    
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
        self.data_dirpath = Path('data/output')
    
    def excute(self):
        pass


if __name__ == '__main__':
    c = ProcessFilesCommand().execute()