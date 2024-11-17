import logging
import copy
from collections import namedtuple
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


class ProductAlreadyAddedException(Exception):
    """When trying to add the same product more than once, it'll alert you."""


class CannotCheckoutMoreThanStockQTException(Exception):
    """When trying to add the same product more than once, it'll alert you."""




@dataclass()
class Product:
    """A product from the inventory"""

    n_article: str
    designation: str
    groupe_code: str
    stock_qt: int
    prix: float
    returned: bool = False

    def __str__(self):
        return f"Produit {self.n_article} ({self.prix} DZD | {self.stock_qt} Units)"

    def __repr__(self):
        return self.__str__()

    def __post_init__(self):
        self.stock_qt_intial: int = copy.copy(self.stock_qt)

    def __eq__(self, value):
        if not isinstance(value, Product):
            raise TypeError(f'{type(value)} not supported')
        return self.n_article == value.n_article

    def __hash__(self):
        return hash(self.n_article)


@dataclass
class MergedProduct:
    code: str
    p_C: Product
    p_I: Product
    p_O: Product


@dataclass
class Sale:
    '''Class to hold final data returned after calculating the quantities.'''
    product: Product
    units_sold: int = 0

    @property
    def sale_total_amount(self):
        return self.product.prix * self.units_sold


@dataclass
class ShowRoom:
    refrence: str
    assigned_total_sales: float
    sales: list[Sale] = field(default_factory=list)

    def __str__(self):
        return f"Showroom {self.refrence} ({self.assigned_total_sales} DZD)"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, value):
        if not isinstance(value, ShowRoom):
            raise TypeError(f'{type(value)} not supported')
        return self.refrence == value.refrence

    def __hash__(self):
        return hash(self.refrence)

    def add_sale(self, product: Product) -> None:
        self.sales.append(product)

    @property
    def calculated_total_sales(self) -> bool:
        return sum(s.sale_total_amount for s in self.sales)


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
                    if p.stock_qt - s.units_sold < 0:
                        raise CannotCheckoutMoreThanStockQTException(
                            f'{p}:cannot take {s.units_sold} out of {p.stock_qt}')
                    p.stock_qt -= s.units_sold
                    break
    
    def _handle_returned_items(self):
        for p in self.products:
            if p.stock_qt < 0:
                p.returned = True
                p.prix = -1 * p.prix
                p.stock_qt = -1 * p.stock_qt

    def get_products(self, all: bool=False) -> list[Product]:
        if all:
            return self.products
        return [p for p in self.products if p.stock_qt > 0]

    def has_products(self):
        return self.get_products() != []
    

    def merge_products(self, products: list[Product]) -> list[Product]:
        pass


    def split_products(self, sales: list[Sale]) -> list[Product]:
        return ProductMergeSplitTransformer.split_product(
            sales=sales,
            all_products=self.products
        )


class ProductMergeSplitTransformer:

    @staticmethod
    def _find_product_stem(n_article: str, prefix: list[str]) -> str|None:
        n_article = n_article.replace(' ', '').strip()
        if any(n_article.endswith(pfix) for pfix in prefix):
            return n_article[:-2]
        return None

    @staticmethod
    def split_product(sales: list[Sale], all_products:list[Product]) -> list[Product]:
        new_sales: list[Sale] = []
        for s in sales:
            code = ProductMergeSplitTransformer._find_product_stem(s.product.n_article, prefix=['-C'])
            if code: 
                for p_inv in all_products:
                    code_inv = ProductMergeSplitTransformer._find_product_stem(p_inv.n_article, prefix=['-O', '-I'])
                    if code == code_inv:
                        p = copy.copy(p_inv)
                        p.stock_qt += s.product.stock_qt
                        p.stock_qt_intial += s.product.stock_qt_intial
                        new_sales.append(Sale(
                            product=p,
                            units_sold=s.units_sold
                        ))
                s.units_sold = 0
        return sales + new_sales



def gen_test_product(
        n_article: str = 'test',
        designation='test designation',
        stock_qt: int = 10,
        prix: float = 10,
        returned: bool = False
):
    return Product(
        n_article=n_article,
        designation=designation,
        groupe_code='',
        stock_qt=stock_qt,
        prix=prix,
        returned=returned,
    )


if __name__ == "__main__":
    pass
