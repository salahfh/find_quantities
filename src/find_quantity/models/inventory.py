import copy
from dataclasses import dataclass

from find_quantity.models.package import Package, PackageConstractor
from find_quantity.models.product import Product
from find_quantity.acquire_data.read_merge_configs import MergeRule, PackageDefinitionsConstructor


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

    @property
    def corrected_unit_sold(self):
        """
        TEMPORARY FIX:
        This hacky fix to show negative quantity for returned products in the reports.
        It should be handled at the level of the inventory class
        """
        if self.product.prix < 0:
            return -1 * self.units_sold
        return self.units_sold


class Inventory:
    def __init__(
        self,
        merge_rules: list[MergeRule],
    ):
        self.merge_rules = merge_rules
        self.products: set[Product] = None
        self.packages: list[Package] = None

    def add_products(self, products: list[Product]):
        products_inv: set[Product] = set()
        for p in products:
            for p_inv in products_inv:
                if p_inv == p:
                    p_inv.stock_qt += p.stock_qt
                    p_inv.stock_qt_intial += p.stock_qt
                    break
            else:
                products_inv.add(copy.copy(p))
        self.products = products_inv
        self._handle_returned_items()
        self.packages = self.__constuct_packages()
        return self.products

    def update_quantities(self, sales: list[Sale]):
        for s in sales:
            for p in self.products:
                if s.product == p:
                    p.update_qt_stock(qt=s.units_sold, operation="Checkout")
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

    def get_packages(self, all: bool = False) -> list[Package]:
        if all:
            return self.packages
        return sorted(
            tuple(p for p in self.packages if p.stock_qt > 0),
            key= lambda p: len(p.sub_products), 
            reverse=True)

    def add_products_from_sales(self, sales: list[Sale]) -> None:
        products = list()
        for s in sales:
            p = copy.copy(s.product)
            p.stock_qt = s.units_sold
            products.append(p)
        self.products = self.add_products(products=products)
        self.packages: list[Package] = self.__constuct_packages()

    def __constuct_packages(self):
        n_articles = [p.n_article for p in self.products]
        package_definitions = PackageDefinitionsConstructor(
            self.merge_rules
        ).make_package_definitions(product_n_articles=n_articles)
        pkc = PackageConstractor(
            products=self.products, package_definitions=package_definitions
        )
        packages = pkc.construct_packages()
        return packages

    def record_sale(self, qt: int, package: Package) -> list[Sale]:
        """Create sale object and return them from here"""
        sales = []
        package.update_qt_stock(qt=qt, operation="Checkout")
        for product in package.sub_products:
            s = Sale(
                product=product,
                units_sold=qt,
            )
            sales.append(s)
        return sales
