from collections import defaultdict
from pathlib import Path
from find_quantity.model import Product, ShowRoom
from find_quantity.commons import IOTools


WORKING_DIR = Path(r'data')
    

@IOTools.from_csv()
def extract_products(data: list[dict], path: Path = WORKING_DIR / 'produits.csv') -> dict[str, list[Product]]:
    values = defaultdict(list)
    for row in data:
        p = Product(
            n_article=row['n_article'],
            designation=row['designation'],
            groupe_code=row['groupe_code'],
            prix=row['prix'],
            stock_qt=row['stock_qt'],
        )
        values[row['mois']].append(p)
    return values


@IOTools.from_csv()
def extract_showrooms(data:list[dict], path: Path=WORKING_DIR / 'showrooms.csv') -> dict[str, list[ShowRoom]]:
    values = defaultdict(list)
    for row in data:
        s = ShowRoom(
            refrence=row['refrence'],
            assigned_total_sales=row['assigned_total_sales'],
        )
        values[row['mois']].append(s)
    return values


if __name__ == '__main__':
    produit = extract_products()
    showrooms = extract_showrooms()
    print(showrooms)
