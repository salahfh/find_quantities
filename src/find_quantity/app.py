from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.model import Solver
from find_quantity.report import Report

def main():
    filepath = Path(r'data\produits.csv')
    products = extract_products(filepath=filepath)
    filepath = Path(r'data\showrooms.csv')
    showrooms = extract_showrooms(filepath=filepath)
    solver = Solver()

    for i, (s_list, p_list) in enumerate(zip(showrooms.values(), products.values())):
        month = i+1
        p_list = ProductTransformer(products=p_list).transform()
        s_list = ShowroomTransformer(showrooms=s_list).transform()
        print(len(p_list), len(s_list))
        for p in p_list:
            solver.add_product(p)
        # solver.products = p_list
        for s in s_list[0:1]:
            solver.add_showroom(s)
        # solver.showrooms = s_list

        solver.calculate_quantities()
        for sh in s_list:
            print(f'{sh.refrence}: total sales: {sum((s.sale_total_amount for s in sh.sales))}')
            for sale in sh.sales:
                print(f'\t{sale.product.n_article}: (Q) {sale.units_sold} x (P) {sale.product.prix} = {sale.sale_total_amount}')
            if solver.is_solution_feasable():
                report = Report(month=month, showroom=sh)
                report.write_csv_report()
        break



if __name__ == '__main__':
    main()