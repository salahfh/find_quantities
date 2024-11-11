from find_quantity.model import Product, ShowRoom

class Transformers:
    def _fix_prices(self, price: str):
        for char in [' ', '-', ',']:
            price = price.replace(char, '')
        if price == '':
            return 0
        return float(price)
    
class ProductTransformer(Transformers):
    def __init__(self, products: list[Product]):
        self.products = products
    
    def _fix_stock_qt(self, stock: str):
        return int(stock)

    def _assign_max_sales_percentage(self, percentage: float = .01) -> float:
        return percentage

    def transform(self):
        cleaned = []
        for p in self.products:
            p = Product(
                n_article=p.n_article,
                designation=p.designation,
                groupe_code=p.groupe_code,
                stock_qt=self._fix_stock_qt(p.stock_qt),
                prix=self._fix_prices(p.prix),
                max_sales_precentage_from_total_sales=self._assign_max_sales_percentage(),
            )
            cleaned.append(p)
        return cleaned


class ShowroomTransformer(Transformers):
    def __init__(self, showrooms: list[ShowRoom]):
        self.showrooms = showrooms

    def transform(self):
        cleaned = []
        for s in self.showrooms:
            s = ShowRoom(
                refrence=s.refrence,
                assigned_total_sales=self._fix_prices(s.assigned_total_sales)
            )
            cleaned.append(s)
        return cleaned
