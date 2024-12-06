from find_quantity.model import Product, gen_test_product


class Package:
    def __init__(self, n_article: str, sub_products: list[Product]):
        self.n_article = n_article
        self.sub_products = sub_products
        self._product = None
    
    @property
    def product(self):
        if self._product is None:
            self._product = self.__construct_merged_product()
        return self._product

    def __construct_merged_product(self):
        stock_qt = self.__calculate_stock_qt()
        self.__update_sub_products_stock(max_stock=stock_qt)
        p = Product(
                n_article=f'PK-{self.n_article}',
                designation=f'Package of {[p.n_article for p in self.sub_products]}',
                groupe_code=' and '.join({p.groupe_code for p in self.sub_products}),
                stock_qt=stock_qt,
                prix=sum([p.prix for p in self.sub_products]),
                tee=0,
                rta=0,
            )
        return p
        
    def __calculate_stock_qt(self) -> int:
        share_stock = min([p.stock_qt for p in self.sub_products])
        assert share_stock > 0, 'Share stock is below or equal to zero'
        return share_stock

    def __update_sub_products_stock(self, max_stock) -> None:
        for p in self.sub_products:
            p.update_qt_stock(max_stock, operation='Checkout')
    
    def disolve_package(self) -> list[Product]:
        for p in self.sub_products:
            p.update_qt_stock(qt=self.product.stock_qt, operation='Insert')
        self.product.stock_qt = 0
        return self.sub_products

    def __repr__(self):
        return f'Package {self.n_article} containing: {[p for p in self.sub_products]}'


class PackageConstractor:
    pass
# class ProductsToCombine:
#     patterns: list[Callable] = lambda x: x

# p: CMD211
# p: CRG14CL1N
# p: CRG14CL1NCMD
# p: AE-X12BBAL

# AS-12UW4SGETU00-I
# AS-12UW4SGETU00-O

# AY-X12BBAL
# AE-X12BBAL




def test_two_products_merged_in_one_package():
    p1 = gen_test_product(n_article='AY-X12BBAL', prix=12, stock_qt=2)
    p2 = gen_test_product(n_article='AE-X12BBAL', prix=8, stock_qt=5)

    pk = Package('X12BBAL', sub_products=[p1, p2])

    assert pk.product.stock_qt == 2
    assert pk.product.prix == 20
    assert p1.stock_qt == 0
    assert p2.stock_qt == 3

def test_disolve_package_to_orginal_products():
    p1 = gen_test_product(n_article='AY-X12BBAL', prix=12, stock_qt=5)
    p2 = gen_test_product(n_article='AE-X12BBAL', prix=8, stock_qt=8)
    pk = Package('X12BBAL', sub_products=[p1, p2])
    pk.product.stock_qt -= 2

    pk.disolve_package()

    assert pk.product.stock_qt == 0
    assert p1.stock_qt == 3
    assert p2.stock_qt == 6


if __name__ == '__main__':
    test_two_products_merged_in_one_package()
    test_disolve_package_to_orginal_products()