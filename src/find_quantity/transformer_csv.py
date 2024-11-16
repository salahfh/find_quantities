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
        self.merged_products = None

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

        merged_products: dict[dict[str, list[Product]]] = defaultdict(dict)
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

                merged_products[stem]['split'] = [p1, p2]
                merged_products[stem]['merged'] = [p3]
        self.products = cleaned_products
        self.merged_products = merged_products

    def split_merged_products(self,
                              sales_products: list[Product],
                              all_products: list[Product]
                              ) -> list[Product]:
        # find the products that are combined
        combined_products: list[Product] = []
        split_products: list[Product] = []
        # find their equivalant
        for p in sales_products:
            code = self._get_product_stem(code=p.n_article, prefixes=['-C'])
            if code:
                if p.n_article.startswith(code):
                    combined_products.append(p)
        for p_inv in all_products:
            code = self._get_product_stem(code=p.n_article, prefixes=['-I', '-O'])
            if code:
                if p_inv.n_article.startswith(code):
                    # combined_products.append(p)
                    print(p_inv)


class Transformers:
    def _fix_numeric_fields(self, price: str):
        for char in [' ', ',']:
            price = str(price).replace(char, '')
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

    def clean_fields(self) -> list[Product]:
        cleaned = []
        for p in self.products:
            p = Product(
                n_article=self.strip_white_spaces(p.n_article),
                designation=self.strip_white_spaces(p.designation),
                groupe_code=self.strip_white_spaces(p.groupe_code),
                stock_qt=self._fix_stock_qt(p.stock_qt),
                prix=self._fix_numeric_fields(p.prix),
            )
            cleaned.append(p)
        self.products = cleaned

    def transform(self) -> list[Product]:
        self.clean_fields()
        self.merge_indoor_outdoor_units()
        return self.products

    def load(self) -> list[Product]:
        self.clean_fields()
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

    def load(self) -> list[ShowRoom]:
        return self.transform()
