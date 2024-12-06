import copy
from dataclasses import dataclass

from find_quantity.models.product import Product, CannotCheckoutMoreThanStockQTException


@dataclass
class Sale:
    """Class to hold final data returned after calculating the quantities."""

    product: Product
    units_sold: int = 0

    def __repr__(self):
        return f"Sale {self.product.n_article} (Sold: {self.units_sold})"

    @property
    def sale_total_amount(self):
        return self.product.prix * self.units_sold

    @property
    def total_ttc(self) -> float:
        return self.product.prix_ttc * self.units_sold


class Inventory:
    def __init__(self, products: list[Product]):
        self.products: set[Product] = self._add_products(products)
        self._handle_returned_items()

    def _add_products(self, products: list[Product]):
        products_inv: set[Product] = set()
        for p in products:
            for p_inv in products_inv:
                if p_inv == p:
                    p_inv.stock_qt += p.stock_qt
                    p_inv.stock_qt_intial += p.stock_qt
                    break
            else:
                products_inv.add(copy.copy(p))
        return products_inv

    def update_quantities(self, sales: list[Sale]):
        for s in sales:
            for p in self.products:
                if s.product == p:
                    # TODO: Refactor this part to Product.udpate
                    if (p.stock_qt - s.units_sold) < 0:
                        raise CannotCheckoutMoreThanStockQTException(
                            f"{p}:cannot take {s.units_sold} out of {p.stock_qt}"
                        )
                    p.stock_qt -= s.units_sold
                    break

    def _handle_returned_items(self):
        for p in self.products:
            if p.stock_qt < 0:
                p.returned = True
                p.prix = -1 * p.prix
                p.stock_qt = -1 * p.stock_qt

    def get_products(self, all: bool = False) -> list[Product]:
        if all:
            return self.products
        return tuple(p for p in self.products if p.stock_qt > 0)

    def add_products_from_sales(self, sales: list[Sale]) -> None:
        products = list()
        for s in sales:
            p = copy.copy(s.product)
            p.stock_qt = s.units_sold
            products.append(p)
        self.products = self._add_products(products=products)

    def __constuct_packages(self):
        self.packages = []
        pass

    def __desolve_packages(self):
        pass

    def record_sale(self, qt: int, product: Product):
        """Create sale object and return them from here"""
        """Record a list of all sales made as well"""
        self.global_sales = []
        pass
