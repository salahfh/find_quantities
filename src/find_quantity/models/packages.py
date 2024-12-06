from typing import Literal
from find_quantity.models.product import Product, gen_test_product


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


def test_package_construction_from_definition():
    package_definitions = [
        ("RGK212N", "CRG10CL1G", "CRG10CL1N", "CRG1400"),
        ("CMD211", "CRG14CL1N", "CRG14CL1NCMD"),
        ("AS-12UW4SGETU00-I", "AS-12UW4SGETU00-O"),
        ("NCE1100", "NCE1100CMD"),
        ("AY-X12BBAL", "AE-X12BBAL"),
        ("NCE185CMD",),
    ]
    products = []
    for pkd in package_definitions:
        products += [gen_test_product(n_article=deff) for deff in pkd]

    pks = PackageConstractor(products, package_definitions).construct_packages()

    assert len(pks) == 6


def test_pacakges_with_products_that_have_left_overs():
    product_qt = [
        ("RGK212N", 8),
        ("CRG10CL1G", 10),
        ("CRG10CL1N", 10),
        ("CRG1400", 10),
    ]
    package_definitions = [tuple(p[0] for p in product_qt)]
    products = []
    for p, qt in product_qt:
        products.append(gen_test_product(n_article=p, stock_qt=qt))

    pks = PackageConstractor(products, package_definitions).construct_packages()

    assert len(pks) == 4


def test_not_enough_quantity_to_make_package_with_incomplete_packages_allowed():
    product_qt = [
        ("RGK212N", 0),
        ("CRG10CL1G", 10),
        ("CRG10CL1N", 10),
        ("CRG1400", 10),
    ]
    package_definitions = [tuple(p[0] for p in product_qt)]
    products = []
    for p, qt in product_qt:
        products.append(gen_test_product(n_article=p, stock_qt=qt))

    pks = PackageConstractor(
        products, package_definitions, allow_incomplete_packages=True
    ).construct_packages()
    assert len(pks) == 1


def test_not_enough_quantity_to_make_package_with_incomplete_packages_not_allowed():
    product_qt = [
        ("RGK212N", 0),
        ("CRG10CL1G", 10),
        ("CRG10CL1N", 10),
        ("CRG1400", 10),
    ]
    package_definitions = [tuple(p[0] for p in product_qt)]
    products = []
    for p, qt in product_qt:
        products.append(gen_test_product(n_article=p, stock_qt=qt))

    pks = PackageConstractor(
        products, package_definitions, allow_incomplete_packages=False
    ).construct_packages()
    assert len(pks) == 3


def test_pacakges_with_products_define_in_more_than_one_package():
    package_definitions = [
        ("CMD211", "CRG14CL1N", "CRG14CL1NCMD"),
        ("AY-X12BBAL", "AE-X12BBAL", "CMD211"),
    ]
    product_qt = [
        ("CMD211", 10),
        ("CRG14CL1N", 10),
        ("CRG14CL1NCMD", 10),
        ("AY-X12BBAL", 10),
        ("AE-X12BBAL", 10),
        # ("CMD211", 10),
    ]
    products = []
    for p, qt in product_qt:
        products.append(gen_test_product(n_article=p, stock_qt=qt))

    pks = PackageConstractor(
        products, package_definitions, allow_incomplete_packages=True
    ).construct_packages()
    assert len(pks) == 2

    pks = PackageConstractor(
        products, package_definitions, allow_incomplete_packages=False
    ).construct_packages()
    assert len(pks) == 3

def test_pacakges_with_no_package_rules_defined():
    package_definitions = [ ]
    product_qt = [
        ("CMD211", 10),
        ("CRG14CL1N", 10),
        ("CRG14CL1NCMD", 10),
        ("AY-X12BBAL", 10),
        ("AE-X12BBAL", 10),
    ]
    products = []
    for p, qt in product_qt:
        products.append(gen_test_product(n_article=p, stock_qt=qt))

    pks = PackageConstractor(
        products, package_definitions, allow_incomplete_packages=True
    ).construct_packages()
    assert len(pks) == 5


if __name__ == "__main__":
    test_package_construction_from_definition()
    test_pacakges_with_products_that_have_left_overs()
    test_not_enough_quantity_to_make_package_with_incomplete_packages_allowed()
    test_not_enough_quantity_to_make_package_with_incomplete_packages_not_allowed()
    test_pacakges_with_products_define_in_more_than_one_package()
    test_pacakges_with_no_package_rules_defined()
