import copy
from typing import Literal
from dataclasses import dataclass


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
    tee: float
    rta: float
    tva: float = 0.19
    returned: bool = False

    @property
    def prix_ttc(self) -> float:
        m_tee = self.prix * self.tee / 100
        m_tva = (self.prix + m_tee) * self.tva
        return round(self.prix + m_tee + m_tva + self.rta, 2)

    def __str__(self):
        return f"Produit {self.n_article} ({self.prix} DZD | {self.stock_qt} Units)"

    def __repr__(self):
        return self.__str__()

    def __post_init__(self):
        self.stock_qt_intial: int = copy.copy(self.stock_qt)

    def __eq__(self, value):
        if not isinstance(value, Product):
            raise TypeError(f"{type(value)} not supported")
        return self.n_article == value.n_article

    def __hash__(self):
        return hash(self.n_article)

    def update_qt_stock(
        self, qt: int, operation: Literal["Checkout", "Insert"] = "Checkout"
    ) -> None:
        if operation == "Checkout":
            qt = -qt
        if self.stock_qt + qt < 0:
            raise CannotCheckoutMoreThanStockQTException
        self.stock_qt += qt


def gen_test_product(
    n_article: str = "test",
    designation="test designation",
    stock_qt: int = 10,
    prix: float = 10,
    rta=0,
    tee=0,
    returned: bool = False,
):
    return Product(
        n_article=n_article,
        designation=designation,
        groupe_code="",
        stock_qt=stock_qt,
        prix=prix,
        rta=0,
        tee=0,
        returned=returned,
    )
