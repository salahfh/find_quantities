from pathlib import Path
from find_quantity.extract_csv import extract_products
from find_quantity.transformer_csv import ProductTransformer


def main():
    filepath = Path(r'data\produits.csv')
    products = extract_products(filepath=filepath)

    for i, p_list in enumerate(products.values()):
        month = i+1
        print(f'Month {month}')
        p_transfomer = ProductTransformer(products=p_list)
        p_list = p_transfomer.transform()
        p_transfomer.split_merged_products(
            products=p_list, all_inventory_products=p_list)
        # for p in p_transfomer.products:
        #     # print(p)

        break


if __name__ == '__main__':
    main()
