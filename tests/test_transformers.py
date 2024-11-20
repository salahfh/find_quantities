from find_quantity.model import Product, Sale, gen_test_product, ProductMergeSplitTransformer
from find_quantity.transformer_csv import MergeSplitProductsMixin


def get_sale_of_product(product: Product, sales: list[Sale]) -> Sale:
    for s in sales:
        if s.product == product:
            return s


class TestMergeProducts:
    def test_merge_two_products_I_O_equal_quantity(self):
        p1 = gen_test_product(n_article='test-I', stock_qt=10)
        p2 = gen_test_product(n_article='test-O', stock_qt=10)
        p3 = gen_test_product(n_article='test-C', prix=20, stock_qt=0)
        m = MergeSplitProductsMixin(products=[p1, p2])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 3
        for p in m.products:
            assert p.n_article in [p1.n_article, p2.n_article, p3.n_article]
        assert p3.prix == 20

    def test_merge_two_products_I_O_not_equal_quantity(self):
        p1 = gen_test_product(n_article='test-I', prix=10, stock_qt=20)
        p2 = gen_test_product(n_article='test-O', prix=10, stock_qt=10)
        p3 = gen_test_product(n_article='test-C', prix=20, stock_qt=10)

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
        p1 = gen_test_product(n_article='test-I', stock_qt=20)
        m = MergeSplitProductsMixin(products=[p1])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 1

        p3 = gen_test_product(n_article='test-C', stock_qt=10, prix=30)

        for p in m.products:
            assert p.n_article not in [p3.n_article]

    def test_multiple_non_mergeable_products(self):
        p1 = gen_test_product(n_article='test-J', stock_qt=20)
        p2 = gen_test_product(n_article='test-K', stock_qt=20)
        p3 = gen_test_product(n_article='test-T', stock_qt=20)
        m = MergeSplitProductsMixin(products=[p1, p2, p3])
        m.merge_indoor_outdoor_units()
        assert len(m.products) == 3

        for p in m.products:
            assert p.stock_qt == 20

class TestSplitProducts:

    def test_split_one_product(self):
        p1 = gen_test_product(n_article='test-I', designation='test-I', prix=10, stock_qt=0)
        p2 = gen_test_product(n_article='test-O', designation='test-O', prix=20, stock_qt=0)
        p3 = gen_test_product(n_article='test-C', designation='test-c', prix=30, stock_qt=10)
        s3 = Sale(
            product=p3,
            units_sold=5,
        )
        sales: list[Sale] = ProductMergeSplitTransformer.split_product(
            sales=[s3],
            all_products=[p1, p2]
        )
        assert len(sales) == 3

        for s in sales:
            if s.product == p1:
                assert s.product.stock_qt == p3.stock_qt
                assert s.product.designation == p1.designation
                assert s.product.prix == p1.prix 
                assert s.units_sold == 5
            if s.product == p2:
                assert s.product.stock_qt == p3.stock_qt
                assert s.product.designation == p2.designation
                assert s.product.prix == p2.prix 
                assert s.units_sold == 5
            if s.product == p3:
                assert s.units_sold == 0
        


    def test_split_one_product_with_product_has_some_left_over_stock(self):
        p1 = gen_test_product(n_article='test-I', designation='test-I', prix=10, stock_qt=5)
        p2 = gen_test_product(n_article='test-O', designation='test-O', prix=20, stock_qt=0)
        p3 = gen_test_product(n_article='test-C', designation='test-c', prix=30, stock_qt=10)
        s3 = Sale(
            product=p3,
            units_sold=5,
        )
        sales: list[Sale] = ProductMergeSplitTransformer.split_product(
            sales=[s3],
            all_products=[p1, p2]
        )
        assert len(sales) == 3

        for s in sales:
            if s.product == p1:
                assert s.product.stock_qt == 15 #p3.stock + p1.stock
                assert s.units_sold == 5
            if s.product == p2:
                assert s.product.stock_qt == p3.stock_qt
                assert s.units_sold == 5
            if s.product == p3:
                assert s.units_sold == 0


    def test_split_one_product_assert_copies_of_products_are_changed_not_original_products(self):
        p1 = gen_test_product(n_article='test-I', designation='test-I', prix=10, stock_qt=0)
        p2 = gen_test_product(n_article='test-O', designation='test-O', prix=20, stock_qt=0)
        p3 = gen_test_product(n_article='test-C', designation='test-c', prix=30, stock_qt=10)
        s3 = Sale(
            product=p3,
            units_sold=5,
        )
        _: list[Sale] = ProductMergeSplitTransformer.split_product(
            sales=[s3],
            all_products=[p1, p2]
        )

        assert p1.stock_qt == 0
        assert p2.stock_qt == 0
        assert p3.stock_qt == 10

        assert p1.prix == 10
        assert p2.prix == 20
        assert p3.prix == 30

    def test_split_one_product_while_other_remain_untouched(self):
        p1 = gen_test_product(n_article='test-I', designation='test-I', prix=10, stock_qt=0)
        p2 = gen_test_product(n_article='test-O', designation='test-O', prix=20, stock_qt=0)
        p3 = gen_test_product(n_article='test-C', designation='test-C', prix=30, stock_qt=10)
        p4 = gen_test_product(n_article='test-D', designation='test-D', prix=40, stock_qt=12)
        s3 = Sale(
            product=p3,
            units_sold=5,
        )
        s4 = Sale(
            product=p4,
            units_sold=10
        )
        sales: list[Sale] = ProductMergeSplitTransformer.split_product(
            sales=[s3, s4],
            all_products=[p1, p2, p3, p4]
        )
    
        assert len(sales) == 4

        p4_s = get_sale_of_product(p4, sales)
        assert p4_s.product.stock_qt == 12 
        assert p4_s.units_sold == 10

    def test_split_product_when_there_sales_from_combined_and_non_combined_products(self):
        p1 = gen_test_product(n_article='test-I', designation='test-I', prix=30, stock_qt=0)
        p2 = gen_test_product(n_article='test-O', designation='test-O', prix=30, stock_qt=10)
        p3 = gen_test_product(n_article='test-C', designation='test-C', prix=30, stock_qt=15)
        s2 = Sale(
            product=p2,
            units_sold=5,
        )
        s3 = Sale(
            product=p3,
            units_sold=5,
        )

        sales: list[Sale] = ProductMergeSplitTransformer.split_product(
            sales=[s2, s3],
            all_products=[p1, p2, p3]
        )

        s_p1 = get_sale_of_product(p1, sales)
        s_p2 = get_sale_of_product(p2, sales)
        s_p3 = get_sale_of_product(p3, sales)
        assert s_p1.product.stock_qt == 15
        assert s_p2.product.stock_qt == 20  # inital stock + combined stock - s1.units_sold - s2.units_sold
        assert s_p3.units_sold == 0

