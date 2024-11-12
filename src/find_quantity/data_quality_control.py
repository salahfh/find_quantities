from pathlib import Path
from find_quantity.extract_csv import extract_products
from find_quantity.transformer_csv import ProductTransformer


def main():
    filepath = Path(r'data\produits.csv')
    products = extract_products(filepath=filepath)

    for i, p_list in enumerate(products.values()):
        month = i+1
        print(f'Month {month}')
        p_list = ProductTransformer(products=p_list).transform()

    
if __name__ == '__main__':
    main()