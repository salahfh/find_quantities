import pytest

from find_quantity.model import ShowRoom, Product, gen_test_product, Sale
from find_quantity.solver import Solver, SolverRunner


class TestSolver:
    def test_simple_solver_with_4_products(self):
        sh = ShowRoom(refrence="sh-bba", assigned_total_sales=10)
        p1 = Product(
            designation=f"p{1}",
            n_article=f"Product_{1}",
            stock_qt=1000,
            groupe_code='P1',
            prix=1,
        )
        p2 = Product(
            designation=f"p{2}",
            n_article=f"Product_{2}",
            stock_qt=1000,
            groupe_code='P1',
            prix=3,
        )
        p3 = Product(
            designation=f"p{3}",
            n_article=f"Product_{3}",
            stock_qt=5000,
            groupe_code='P1',
            prix=3,
        )
        p4 = Product(
            designation=f"p{4}",
            n_article=f"Product_{4}",
            stock_qt=5000,
            groupe_code='P2',
            prix=3,
        )

        expected_sales = sh.assigned_total_sales

        ps = tuple([p1, p2, p3, p4])
        solver = Solver(ps)
        solver.calculate_quantities(showroom=sh, max_product_sales_percentage=.9, tolerance=0)

        assert expected_sales == sh.calculated_total_sales

    @pytest.mark.skip('Rewrite this test for solver class')
    def test_calc_quantity_4_products_of_same_price_sold_with_equal_percentages(
        self,
        showroom: ShowRoom,
    ):
        products_quantity = 4
        for _ in range(products_quantity):
            p = gen_test_product()
            showroom.add_product(p)

        showroom.calculate_quantities()
        assert sum((s.units_sold for s in showroom.sales)) == 10
        assert sum((s.sale_total_amount for s in showroom.sales)) == 100

    @pytest.mark.skip('Rewrite this test for solver class')
    def test_calc_quantity_for_4_products_of_same_price_sold_with_custom_percentages(
        self,
        showroom: ShowRoom,
    ):
        products_quantity = 4
        shares = [0.2, 0.1, 0.2, 0.5]
        for i in range(products_quantity):
            p = Product(
                designation=f"Refrence_{i}",
                n_article=f"Product_{i}",
                stock_qt=10,
                groupe_code='P1',
                prix=10,
                max_sales_precentage_from_total_sales=shares.pop(),
            )
            showroom.add_product(p)
        showroom.calculate_quantities()
        assert sum((s.sale_total_amount for s in showroom.sales)) == 100
        assert sum((s.units_sold for s in showroom.sales)) == 10


class TestSolverRunner:
    def test_assign_new_sale_value_but_product_were_sold(self):
        # arrange
        s1 = ShowRoom(refrence='sh1', assigned_total_sales=100)
        s2 = ShowRoom(refrence='sh2', assigned_total_sales=50)
        s3 = ShowRoom(refrence='sh3', assigned_total_sales=100)
        s4 = ShowRoom(refrence='sh4', assigned_total_sales=250)
        all_showrooms = [s1, s2, s3, s4]
        unsolved_showrooms = [s1, s2, s3, s4]
        sr = SolverRunner(inventory='')
        
        # act
        _ = sr.assign_new_sale_values(unsolved_showrooms,all_showrooms)
        assert round(sum([sh.assigned_total_sales for sh in all_showrooms]), 0) == 500

             
        # assert
        assert s1.assigned_total_sales != 100
        assert s2.assigned_total_sales != 50
        assert s3.assigned_total_sales != 100
        assert s4.assigned_total_sales != 250

    def test_assign_new_sales_to_showrooms_when_showroom_fully_sold(self):
        # arrange
        sale1 = Sale(product=gen_test_product(prix=100), units_sold=1)
        s1 = ShowRoom(refrence='sh1', assigned_total_sales=100)
        s1.add_sale(sale1)
        s2 = ShowRoom(refrence='sh2', assigned_total_sales=50)
        s3 = ShowRoom(refrence='sh3', assigned_total_sales=100)
        s4 = ShowRoom(refrence='sh4', assigned_total_sales=250)
        all_showrooms = [s1, s2, s3, s4]
        unsolved_showrooms = [s2, s3, s4]
        sr = SolverRunner(inventory='')
        
        # act
        _ = sr.assign_new_sale_values(unsolved_showrooms,all_showrooms)

        assert round(sum([sh.assigned_total_sales for sh in all_showrooms]), 0) == 500
             
        # assert
        assert s1.assigned_total_sales == 100
        assert s2.assigned_total_sales != 50
        assert s3.assigned_total_sales != 100
        assert s4.assigned_total_sales != 250

    def test_assign_new_sales_to_showrooms_when_showroom_is_sold_out_partially(self):
        # arrange
        sale1 = Sale(product=gen_test_product(prix=90), units_sold=1)
        s1 = ShowRoom(refrence='sh1', assigned_total_sales=100)
        s1.add_sale(sale1)
        s2 = ShowRoom(refrence='sh2', assigned_total_sales=50)
        s3 = ShowRoom(refrence='sh3', assigned_total_sales=100)
        s4 = ShowRoom(refrence='sh4', assigned_total_sales=250)
        all_showrooms = [s1, s2, s3, s4]
        solved = [s1]
        unsolved_showrooms = [s2, s3, s4]
        sr = SolverRunner(inventory='')
        
        # act
        _ = sr.assign_new_sale_values(unsolved_showrooms,all_showrooms)

        assert round(
            sum([sh.assigned_total_sales for sh in all_showrooms]) -
            sum([abs(sh.assigned_total_sales - sh.calculated_total_sales)
                  for sh in solved]),
                0) == 500
             
        # assert
        assert s1.assigned_total_sales == 100
        assert s2.assigned_total_sales != 50
        assert s3.assigned_total_sales != 100
        assert s4.assigned_total_sales != 250
