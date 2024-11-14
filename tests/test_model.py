import random
from find_quantity.model import (
    Product, ShowRoom, Sale, ProductAlreadyAddedException, Inventory,
    gen_test_product, CannotCheckoutMoreThanStockQTException
)

import pytest


# Delete this function later
def create_product():
    return gen_test_product()


@pytest.fixture
def showroom():
    s = ShowRoom(
        refrence=f"showroom_{random.randint(0, 100)}",
        assigned_total_sales=100,
    )
    return s


class TestProduct:
    def test_product_is_hashable_and_work_with_sets(self):
        p1 = gen_test_product()
        products = set()
        products.add(p1)
        assert len(products) == 1
        products.add(p1)
        assert len(products) == 1
        assert p1 in products

    def test_product_comparaison(self):
        p1 = gen_test_product()
        p2 = gen_test_product(n_article='test 2')
        assert p1 == p1
        assert p1 != p2

    def test_product_can_work_with_sets(self):
        p1 = gen_test_product()
        p2 = gen_test_product(n_article='test 2')
        s = set([p1, p2])
        assert len(s) == 2


class TestInvetory:
    def test_inventory(self):
        p = gen_test_product()
        inv = Inventory(products=[p])
        assert len(inv.products) == 1

    def test_add_same_product_twice_update_stock_quantity(self):
        p = gen_test_product(stock_qt=10)
        inv = Inventory(products=[p, p])
        assert len(inv.get_products()) == 1
        assert inv.get_products()[0].stock_qt == 20

    def test_inventory_update_product_quantity_with_one_sale(self):
        p = gen_test_product()
        inv = Inventory(products=[p])
        s = Sale(
            product=p,
            units_sold=2
        )
        inv.update_quantities(sales=[s])
        for pi in inv.products:
            if pi.designation == p.designation:
                assert pi.stock_qt == 8
                assert pi.stock_qt_intial == 10

    def test_inventory_update_product_quantity_with_multiple_sales(self):
        p = gen_test_product()
        inv = Inventory(products=[p])
        s = Sale(
            product=p,
            units_sold=2
        )
        inv.update_quantities(sales=[s, s])
        for pi in inv.products:
            if pi.designation == p.designation:
                assert pi.stock_qt == 6
                assert pi.stock_qt_intial == 10

    def test_inventory_update_product_quantity_with_no_sales_made(self):
        p = gen_test_product()
        inv = Inventory(products=[p])
        inv.update_quantities(sales=[])
        for pi in inv.products:
            if pi.designation == p.designation:
                assert pi.stock_qt == 10
                assert pi.stock_qt_intial == 10

    def test_inventory_update_product_quantity_with_below_zero(self):
        p = gen_test_product(stock_qt=10)
        inv = Inventory(products=[p])
        s = Sale(
            product=p,
            units_sold=10
        )
        with pytest.raises(CannotCheckoutMoreThanStockQTException):
            inv.update_quantities(sales=[s, s])
        for pi in inv.products:
            if pi.designation == p.designation:
                assert pi.stock_qt == 0
                assert pi.stock_qt_intial == 10

    def test_inventory_returned_item_only(self):
        p = gen_test_product(stock_qt=-1, prix=10)
        inv = Inventory(products=[p])
        assert len(inv.get_products()) == 1
        p_out = inv.get_products()[0]
        assert p_out.returned == True
        assert p_out.stock_qt == 1
        assert p_out.prix == -10

    def test_inventory_returned_and_more_non_return_items(self):
        p = gen_test_product(stock_qt=-1, prix=10)
        p2 = gen_test_product(stock_qt=10)
        inv = Inventory(products=[p, p2])

        assert len(inv.get_products()) == 1
        p_out = inv.get_products()[0]
        assert p_out.returned == False
        assert p_out.stock_qt == 9
        assert p_out.prix == 10

    def test_inventory_more_returned_than_non_return_items(self):
        p = gen_test_product(stock_qt=-10, prix=10)
        p2 = gen_test_product(stock_qt=1)
        inv = Inventory(products=[p, p2])

        assert len(inv.get_products()) == 1
        p_out = inv.get_products()[0]
        assert p_out.returned == True
        assert p_out.stock_qt == 9
        assert p_out.prix == -10

    def test_inventory_update_with_returned_products(self):
        p = gen_test_product(stock_qt=-10)
        inv = Inventory(products=[p])
        s = Sale(
            product=p,
            units_sold=9
        )
        inv.update_quantities(sales=[s])
        for pi in inv.products:
            if pi.designation == p.designation:
                assert pi.stock_qt == 1
                assert pi.stock_qt_intial == -10
