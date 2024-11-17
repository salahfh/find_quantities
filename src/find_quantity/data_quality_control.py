from copy import copy
from pathlib import Path
from find_quantity.extract_csv import extract_products
from find_quantity.transformer_csv import ProductTransformer


def main():
    filepath = Path(r'data\produits.csv')
    filepath_sales = Path(r"C:\Users\saousa\Scripts\MustafaAcc\data\output\2. Calculate\month_1.csv")
    products = extract_products(path=filepath)

    for i, p_list in enumerate(products.values()):
        month = i+1
        print(f'Month {month}')
        p_transfomer = ProductTransformer(products=p_list)
        p_inv = p_transfomer.transform()
        # p_sales = p_transfomer.transform()
        # p_transfomer.split_merged_products(
            # sales_products=p_inv, all_products=p_inv)
        # for p in p_transfomer.products:
        #     # print(p)
        for code, p in p_transfomer.merged_products.items():
            print(code)
            print(p)

        break


if __name__ == '__main__':
    main()
