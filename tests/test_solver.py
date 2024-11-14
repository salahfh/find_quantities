import pytest

from find_quantity.model import ShowRoom, Product, gen_test_product
from find_quantity.solver import Solver


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

        solver = Solver(max_product_sales_percentage=.5)
        solver.add_products([p1, p2, p3, p4])
        solver.add_showroom(sh)
        solver.calculate_quantities()

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
