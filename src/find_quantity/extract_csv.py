import csv
from collections import defaultdict
from pathlib import Path
from find_quantity.model import Product, ShowRoom


class ProductConstructor:
    target_class = Product

    def from_row(self, row: dict[str, str]) -> Product:
        return self.target_class(
            n_article=row['n_article'],
            designation=row['designation'],
            groupe_code=row['groupe_code'],
            prix=row['prix'],
            stock_qt=row['stock_qt'])


class ShowroomContructor:
    target_class = ShowRoom

    def from_row(self, row: dict[str, str]) -> ShowRoom:
        return self.target_class(
            refrence=row['refrence'],
            assigned_total_sales=row['assigned_total_sales'],
        )


class Extract:
    def __init__(self, file_path: Path, constractor: ProductConstructor):
        self.constructor = constractor()
        self.file_path = file_path
    
    def extract(self) -> list[object]:
        values = defaultdict(list)
        with open(self.file_path) as f:
            reader = csv.DictReader(f)
            for line in reader:
                if line.get('mois', None):
                    values[line['mois']].append(self.constructor.from_row(line))
                else:
                    values['mois'].append(self.constructor.from_row(line))
        return values

    
def extract_products(filepath: Path) -> dict[str, list[Product]]:
    e = Extract(file_path=filepath, constractor=ProductConstructor)
    return e.extract()

def extract_showrooms(filepath: Path) -> dict[str, list[ShowRoom]]:
    e = Extract(file_path=filepath, constractor=ShowroomContructor)
    return e.extract()

if __name__ == '__main__':
    filepath = Path(r'data\produits.csv')
    produit = extract_products(filepath=filepath)
    filepath = Path(r'data\showrooms.csv')
    showrooms = extract_showrooms(filepath=filepath)
    print(produit)