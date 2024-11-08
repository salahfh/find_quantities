import logging
from dataclasses import dataclass, field
from typing import Literal
import random

USE_ALL_ITEMS_IN_STOCK = True
RANDOM_QUANTITY_PERCENTAGE = 50


logger = logging.getLogger(__name__)


class ProductAlreadyAdded(Exception):
    """When trying to add the same product more than once, it'll alert you."""

    pass


class NotEnoughQuantityInStock(Exception):
    """When trying to add the same product more than once, it'll alert you."""

    pass


@dataclass(frozen=True)
class Product:
    """Read list of products from the inventory data"""

    refrence: str
    name: str
    stock_qt: int
    price: float
    taxable: bool
    percentage_sales_history: float = 0


@dataclass
class Sale:
    product: Product
    sale_total_amount: float = 0
    _units_sold_adjusted: int = 0

    @property
    def units_sold(self) -> int:
        if self._units_sold_adjusted:
            return self._units_sold_adjusted
        return self.sale_total_amount // self.product.price

    def validate_sale(self) -> None:
        if self.units_sold > self.product.stock_qt:
            raise NotEnoughQuantityInStock


@dataclass
class ShowRoom:
    refrence: str
    location: str
    assigned_total_sales: float
    products: set[Product] = field(default_factory=set)
    sales: list[Sale] = field(default_factory=list)

    def __str__(self):
        return f"Showroom {self.refrence}"

    def __repr__(self):
        return self.__str__()

    def log_message(self, message) -> None:
        logger.debug(f"{self}: {message}")

    @property
    def calc_products_total_sales(self) -> float:
        pass

    def add_product(self, product: Product) -> None:
        if product not in self.products:
            self.products.add(product)
        else:
            self.log_message(f"Product already added: Skipping. {product.name}")
            raise ProductAlreadyAdded

    def __generate_random_product_quantity(self, p: Product) -> int:
        if USE_ALL_ITEMS_IN_STOCK:
            return random.randint(1, p.stock_qt)
        return random.randint(1, p.stock_qt - 3)

    def balance_sales(self) -> None:
        """
        make sure the sum of sale.total_sales * sale.units_sold == self.assigned_total_sales
        Selection Considerations:
        1. Eliminate items out of stock.
        2. Eliminate items with Price more than reminder
        3. Perfer items with more sales and higher stocks than the rest.

        R: Reminder
        T: Total Assigned Sales
        Qi: Quantity of an item i
        Qj: a 2nd Quantity of an Quantity i
        Pi: Price of an item i
        Eps: Epsilion - Margin of error allowed
        1. R = T - SUM(Qi * Pi) + Eps
        2. R = SUM(Qj *Pi) + Eps
        """

        # https://stackoverflow.com/questions/34080486/how-do-a-make-sure-an-arbitrary-number-of-weights-sum-to-1-python
        # raise NotImplementedError
        for s in self.sales:
            if s.validate_sale():
                pass
        pass

    def calculate_sales(
        self, generation_mode: Literal["Equal", "Custom"] = "Equal"
    ) -> None:
        if generation_mode == "Equal":
            self.generate_sales_with_equal_percentages()
        elif generation_mode == "Custom":
            self.generate_sales_with_custom_percentage()
        self.balance_sales()

    def generate_sales_with_custom_percentage(self) -> None:
        for p in self.products:
            s = Sale(
                product=p,
                sale_total_amount=self.assigned_total_sales
                * p.percentage_sales_history,
            )
            self.sales.append(s)

    def generate_sales_with_equal_percentages(self) -> None:
        perc = 100 / len(self.products)
        for p in self.products:
            s = Sale(
                product=p, sale_total_amount=self.assigned_total_sales * perc / 100
            )
            self.sales.append(s)


if __name__ == "__main__":
    pass
