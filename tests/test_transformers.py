from find_quantity.model import Product, Sale, gen_test_product
from find_quantity.transformer_csv import MergeSplitProductsMixin


def get_sale_of_product(product: Product, sales: list[Sale]) -> Sale:
    for s in sales:
        if s.product == product:
            return s


class TestMergeProducts:
    def test_merge_two_products_I_O_equal_quantity(self):
        p1 = gen_test_product(n_article="test-I", stock_qt=10)
        p2 = gen_test_product(n_article="test-O", stock_qt=10)
        p3 = gen_test_product(n_article="test-C", prix=20, stock_qt=0)
        m = MergeSplitProductsMixin(products=[p1, p2])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 3
        for p in m.products:
            assert p.n_article in [p1.n_article, p2.n_article, p3.n_article]
        assert p3.prix == 20

    def test_merge_two_products_I_O_not_equal_quantity(self):
        p1 = gen_test_product(n_article="test-I", prix=10, stock_qt=20)
        p2 = gen_test_product(n_article="test-O", prix=10, stock_qt=10)
        p3 = gen_test_product(n_article="test-C", prix=20, stock_qt=10)

        m = MergeSplitProductsMixin(products=[p1, p2])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 3

        for p in m.products:
            if p.n_article == p1.n_article:
                p1_cleaned = p
            if p.n_article == p2.n_article:
                p2_cleaned = p
            if p.n_article == p3.n_article:
                p3_cleaned = p

        assert p3_cleaned.stock_qt == p3.stock_qt
        assert p1_cleaned.stock_qt == 10
        assert p2_cleaned.stock_qt == 0

        assert p3_cleaned.prix == p3.prix

    def test_merge_one_products_I(self):
        p1 = gen_test_product(n_article="test-I", stock_qt=20)
        m = MergeSplitProductsMixin(products=[p1])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 1

        p3 = gen_test_product(n_article="test-C", stock_qt=10, prix=30)

        for p in m.products:
            assert p.n_article not in [p3.n_article]

    def test_multiple_non_mergeable_products(self):
        p1 = gen_test_product(n_article="test-J", stock_qt=20)
        p2 = gen_test_product(n_article="test-K", stock_qt=20)
        p3 = gen_test_product(n_article="test-T", stock_qt=20)
        m = MergeSplitProductsMixin(products=[p1, p2, p3])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 3

        for p in m.products:
            assert p.stock_qt == 20
