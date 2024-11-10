import random
from find_quantity.model import Product, ShowRoom, Sale, ProductAlreadyAdded

import pytest


def create_product():
    rand = random.randint(1, 100)
    return Product(
        refrence=f"Refrence_{rand}",
        name=f"Product_{rand}",
        stock_qt=10,
        price=10,
        taxable=True,
    )


@pytest.fixture
def showroom():
    s = ShowRoom(
        refrence=f"showroom_{random.randint(0, 100)}",
        location="BBA",
        assigned_total_sales=100,
    )
    return s


@pytest.mark.skip("Test Excpetion if raised or not")
def test_calculated_sales_are_more_than_whats_in_stock(showroom: ShowRoom):
    pass


def test_add_product_to_a_showroom(showroom):
    p = create_product()
    showroom.add_product(p)
    assert len(showroom.products) == 1


def test_add_same_product_twice_raises_an_error(showroom):
    p = create_product()
    showroom.add_product(p)
    with pytest.raises(ProductAlreadyAdded):
        showroom.add_product(p)


def test_calc_quantity_4_products_of_same_price_sold_with_equal_percentages(
    showroom: ShowRoom,
):
    products_quantity = 4
    for _ in range(products_quantity):
        p = create_product()
        showroom.add_product(p)

    showroom.calculate_quantities()
    assert sum((s.units_sold for s in showroom.sales)) == 10
    assert sum((s.sale_total_amount for s in showroom.sales)) == 100


def test_calc_quantity_for_4_products_of_same_price_sold_with_custom_percentages(
    showroom: ShowRoom,
):
    products_quantity = 4
    shares = [0.2, 0.1, 0.2, 0.5]
    for i in range(products_quantity):
        p = Product(
            refrence=f"Refrence_{i}",
            name=f"Product_{i}",
            stock_qt=10,
            price=10,
            taxable=True,
            max_sales_precentage_from_total_sales=shares.pop(),
        )
        showroom.add_product(p)
    showroom.calculate_quantities()
    assert sum((s.sale_total_amount for s in showroom.sales)) == 100
    assert sum((s.units_sold for s in showroom.sales)) == 10
