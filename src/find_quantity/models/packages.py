from typing import Literal
from find_quantity.models.product import Product


ALLOW_INCOMPLETE_PACKAGES = True


class Package:
    """Group one product or more together.

    Update and keep tracks of their quantities.
    """

    def __init__(
        self, sub_products: list[Product], n_article: str = None, stock_lmt: int = None
    ):
        self.sub_products = sub_products
        self.n_article = n_article
        self.stock_qt = stock_lmt

    def update_qt_stock(
        self, qt: int, operation: Literal["Checkout", "Insert"] = "Checkout"
    ) -> None:
        for p in self.sub_products:
            p.update_qt_stock(qt, operation)

    def __repr__(self):
        return f"Package {self.n_article} ({self.stock_qt} Units | {[p.n_article for p in self.sub_products]})"


class PackageConstractor:
    def __init__(
        self,
        products: list[Product],
        package_definitions: list[tuple],
        allow_incomplete_packages: bool = ALLOW_INCOMPLETE_PACKAGES,
    ):
        self.products = {p: p.stock_qt for p in products}
        self.package_definitions = package_definitions
        self.allow_incomplete_packages = allow_incomplete_packages

    def valid_package_definitions(self):
        # no product can exists in multiple packages
        raise NotImplementedError

    def get_products(self) -> list[Product]:
        return [p for p, qt in self.products.items() if qt > 0]

    def deduct_allocated_stock(self, allocated_products: list[Product], qt: int = None):
        for p in allocated_products:
            if qt is None:
                qt = self.products[p]
            self.products[p] -= qt

    def construct_packages(self) -> list[Package]:
        packages = []
        for i, pkd in enumerate(self.package_definitions):
            prods: list[Product] = []
            for defin in pkd:
                for p in self.get_products():
                    if p.n_article == defin:
                        prods.append(p)
            if not self.allow_incomplete_packages:
                if len(pkd) != len(prods):
                    continue
            
            # in case of no product matching package definition is found
            # This is the case of product with zero stock
            if not prods:
                continue

            stock_lmt = min([p.stock_qt for p in prods])
            self.deduct_allocated_stock(allocated_products=prods, qt=stock_lmt)

            pk = Package(sub_products=prods, n_article=f"PKG-{i}", stock_lmt=stock_lmt)
            packages.append(pk)

        # left over products are created into seperate packages
        for p in self.get_products():
            pk = Package(
                sub_products=[p],
                n_article=f"PKG-{p.n_article}",
                stock_lmt=self.products[p],
            )
            packages.append(pk)
            self.deduct_allocated_stock(allocated_products=[p])
        return packages


if __name__ == "__main__":
    pass