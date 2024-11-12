import csv
from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.model import Inventory, ShowRoom
from find_quantity.solver import Solver
from find_quantity.report import Report


def print_calculation_output(showroom: ShowRoom):
    print(f'{showroom.refrence}:')
    sum_cal_sales = sum((s.sale_total_amount for s in showroom.sales))
    solved_correctly = sum_cal_sales == showroom.assigned_total_sales
    difference_sales = abs(sum_cal_sales - showroom.assigned_total_sales)
    ratio_difference = round(abs(difference_sales / showroom.assigned_total_sales), 2)
    print(f'\tCalculated total sales: {sum_cal_sales}')
    print(f'\tAssigned total sales: {showroom.assigned_total_sales}')
    print(f'\tAre they equal? {solved_correctly} ')
    print(f'\tDifference? {ratio_difference} ({difference_sales})')
    return solved_correctly

def main():
    products = extract_products(filepath=Path(r'data\produits.csv'))
    showrooms = extract_showrooms(filepath=Path(r'data\showrooms.csv'))

    report = Report()

    for i, (s_list, p_list) in enumerate(zip(showrooms.values(), products.values())):
        month = i+1
        p_list = ProductTransformer(products=p_list).transform()
        s_list = ShowroomTransformer(showrooms=s_list).transform()
        inv = Inventory(products=p_list)

        for j, sh in enumerate(s_list):
            print('-' * 20)
            print(f'{j} - Products with positive stock: {len(inv.get_products())}')

            solver = Solver()
            for p in inv.get_products():
                solver.add_product(p)
            solver.add_showroom(sh)
            solver.calculate_quantities()
            inv.update_quantities(sales=sh.sales)
            solved_correctly = print_calculation_output(showroom=sh)
            if solver.is_solution_feasable():
                print(f'Was it solved correct? {solved_correctly}')
            else:
                print(f'{sh.refrence}: Cannot resolve it')

            # if solved_correctly:
            report.add_showroom(month=month, showroom=sh)



        with open('data/output/product.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(
                (['Article', 'Initial Quantity', 'Current', 'used']),)
            for p in inv.products:
                writer.writerow(
                    (
                        p.n_article,
                        p.stock_qt_intial,
                        p.stock_qt,
                        p.stock_qt_intial - p.stock_qt
                    ),
                )
        break


if __name__ == '__main__':
    main()
