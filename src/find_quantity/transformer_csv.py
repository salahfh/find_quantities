from find_quantity.model import Product, ShowRoom


class Transformers:
    def _fix_numeric_fields(self, price: str):
        for char, char2 in [(" ", ""), ("%", ""), (",", ".")]:
            price = str(price).replace(char, char2)
        if price in ["", "-"]:
            return 0
        return float(price)

    def strip_white_spaces(self, word: str) -> str:
        return word.strip()


class ProductTransformer(Transformers):
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
                rta=self._fix_numeric_fields(p.rta),
                tee=self._fix_numeric_fields(p.tee),
            )
            cleaned.append(p)
        self.products = cleaned

    def transform(self) -> list[Product]:
        self.clean_fields()
        return self.products

    def load(self) -> list[Product]:
        return self.transform()


class ShowroomTransformer(Transformers):
    def __init__(self, showrooms: list[ShowRoom]):
        self.showrooms = showrooms

    def transform(self) -> list[ShowRoom]:
        cleaned = []
        for s in self.showrooms:
            s = ShowRoom(
                refrence=s.refrence,
                assigned_total_sales=self._fix_numeric_fields(s.assigned_total_sales),
            )
            cleaned.append(s)
        return cleaned

    def load(self) -> list[ShowRoom]:
        return self.transform()
