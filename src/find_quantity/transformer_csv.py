from collections import defaultdict
from find_quantity.model import Product, ShowRoom

MAX_PERCENTAGE_PER_ITEM = .1


class ProductDuplicatedException(Exception):
    pass


class ProductAreAlreadySplit(Exception):
    pass


class MergeSplitProductsMixin:
    '''
    Some products such AC come in two items Ext and Int. 
    This function helps merge them and the split them later.
    '''

    def __init__(self, products: list[Product]):
        self.products = products
        # self.merged_products = None

    def _get_product_stem(self, code: str, prefixes: list[str]) -> str | None:
        code.replace(' ', '').strip()
        if any(code.endswith(postfix) == True for postfix in prefixes):
            return code[:-2]
        return None

    def merge_indoor_outdoor_units(self):
        split_products: dict[str, list[Product]] = defaultdict(list)
        for product in self.products:
            code = self._get_product_stem(
                code=product.n_article, prefixes=['-I', '-O'])
            if code:
                split_products[code].append(product)
            else:
                split_products['others'].append(product)

        # merged_products: dict[dict[str, list[Product]]] = defaultdict(dict)
        cleaned_products: list[Product] = []
        for stem, products in split_products.items():
            if stem == 'others' or \
               len(products) == 1:
                cleaned_products += products
            elif len(products) > 2:
                raise ProductDuplicatedException('Duplicated Values')
            else:
                p1, p2 = products
                shared_stock = min(p1.stock_qt, p2.stock_qt)
                shared_price = abs(p1.prix + p2.prix)
                p3 = Product(
                    n_article=f'{stem}-C',
                    designation=f'{p1.designation} - Combined',
                    groupe_code=p1.groupe_code,
                    prix=shared_price,
                    stock_qt=shared_stock,
                )
                p1.stock_qt = abs(shared_stock - p1.stock_qt)
                p2.stock_qt = abs(shared_stock - p2.stock_qt)
                cleaned_products += [p1, p2, p3]

                # merged_products[stem]['split'] = [p1, p2]
                # merged_products[stem]['merged'] = [p3]
        self.products = cleaned_products
        # self.merged_products = merged_products

    def split_merged_products(self, products: list[Product], all_inventory_products: list[Product]) -> list[Product]:
        for p in products:
            code = self._get_product_stem(code=p.n_article, prefixes=['-C'])
            if code:
                for p_inv in all_inventory_products:
                    if p.n_article.startswith(code) and p == p_inv:
                        print(p)


class Transformers:
    def _fix_numeric_fields(self, price: str):
        for char in [' ', ',']:
            price = price.replace(char, '')
        if price in ['', '-']:
            return 0
        return float(price)

    def strip_white_spaces(self, word: str) -> str:
        return word.strip()


class ProductTransformer(Transformers, MergeSplitProductsMixin):
    def __init__(self, products: list[Product]):
        self.products = products

    def _fix_stock_qt(self, stock: str) -> int:
        return int(self._fix_numeric_fields(stock))

    def _assign_max_sales_percentage(self,
                                     percentage: float = MAX_PERCENTAGE_PER_ITEM) -> float:
        return percentage

    def clean_fields(self) -> list[Product]:
        cleaned = []
        for p in self.products:
            p = Product(
                n_article=self.strip_white_spaces(p.n_article),
                designation=self.strip_white_spaces(p.designation),
                groupe_code=self.strip_white_spaces(p.groupe_code),
                stock_qt=self._fix_stock_qt(p.stock_qt),
                prix=self._fix_numeric_fields(p.prix),
                max_sales_precentage_from_total_sales=self._assign_max_sales_percentage(),
            )
            cleaned.append(p)
        self.products = cleaned

    def transform(self) -> list[Product]:
        self.clean_fields()
        self.merge_indoor_outdoor_units()
        return self.products


class ShowroomTransformer(Transformers):
    def __init__(self, showrooms: list[ShowRoom]):
        self.showrooms = showrooms

    def transform(self) -> list[ShowRoom]:
        cleaned = []
        for s in self.showrooms:
            s = ShowRoom(
                refrence=s.refrence,
                assigned_total_sales=self._fix_numeric_fields(
                    s.assigned_total_sales)
            )
            cleaned.append(s)
        return cleaned
