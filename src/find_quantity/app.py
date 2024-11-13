import csv
from pathlib import Path
from find_quantity.extract_csv import extract_showrooms, extract_products
from find_quantity.transformer_csv import ProductTransformer, ShowroomTransformer
from find_quantity.model import Inventory, ShowRoom
from find_quantity.solver import Solver
from find_quantity.report import Report
from find_quantity.debug import timer


def print_calculation_output(showroom: ShowRoom):
    print(f'{showroom.refrence}:')
    sum_cal_sales = sum((s.sale_total_amount for s in showroom.sales))
    solved_correctly = sum_cal_sales == showroom.assigned_total_sales
    difference_sales = abs(sum_cal_sales - showroom.assigned_total_sales)
    if showroom.assigned_total_sales == 0:
        ratio_difference = 0
    else:
        ratio_difference = round(abs(difference_sales / showroom.assigned_total_sales), 2)

    print(f'\tCalculated total sales: {sum_cal_sales}')
    print(f'\tAssigned total sales: {showroom.assigned_total_sales}')
    print(f'\tAre they equal? {solved_correctly} ')
    print(f'\tDifference? {ratio_difference} ({difference_sales})')
    return solved_correctly


def get_monthly_data(
        product_filepath: Path = Path(r'data\produits.csv'),
        showrooms_filepath: Path=Path(r'data\showrooms.csv'),
        ) -> list[tuple]:

    monthly_data = []
    products = extract_products(filepath=product_filepath)
    showrooms = extract_showrooms(filepath=showrooms_filepath)
    for i, (s_list, p_list) in enumerate(zip(showrooms.values(), products.values())):
        month = i+1
        p_list = ProductTransformer(products=p_list).transform()
        s_list = ShowroomTransformer(showrooms=s_list).transform()
        monthly_data.append((month, p_list, s_list))
    return monthly_data

@timer
def main():
    for month, p_list, s_list in get_monthly_data():

        report = Report()
        inv = Inventory(products=p_list)
        for j, sh in enumerate(s_list):
            print('-' * 20)
            print(f'{j} - Products with positive stock: {len(inv.get_products())}')

            solver = Solver()
            solver.add_products(products=inv.get_products())
            solver.add_showroom(sh)
            solver.calculate_quantities()
            solved_correctly = print_calculation_output(showroom=sh)

            # if solver.is_solution_feasable():
            if solved_correctly:
                # print(f'Was it solved correct? {solved_correctly}')
                inv.update_quantities(sales=sh.sales)
                report.add_showroom(month=month, showroom=sh)
            else:
                print(f'{sh.refrence}: Cannot resolve it')

            # if solved_correctly:
        report.write_remaining_products_report(products=inv.get_products())
        break


if __name__ == '__main__':
    main()
