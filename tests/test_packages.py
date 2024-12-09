from find_quantity.models.package import Package, PackageConstractor
from find_quantity.models.product import gen_test_product


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
    package_definitions = []
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


def test_package_quantities_in_of_split_products():
    package_definitions = []
    p1 = gen_test_product(n_article="AY-X12BBAL", stock_qt=10)
    p2 = gen_test_product(n_article="AE-X12BBAL", stock_qt=20)
    products = [p1, p2]

    pk1 = Package(sub_products=products, stock_lmt=10, n_article="PKG-0")
    pk2 = Package(sub_products=[p2], stock_lmt=10, n_article="PKG-AY-X12BBAL")

    pks = PackageConstractor(
        products, package_definitions, allow_incomplete_packages=True
    ).construct_packages()
    assert len(pks) == 2
    for pk in pks:
        if pk is pk1:
            assert pk.stock_qt == 10
        if pk is pk2:
            assert pk.stock_qt == 10
