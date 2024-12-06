from dataclasses import dataclass

from find_quantity.models.product import Product
from find_quantity.models.inventory import Sale, Inventory
from find_quantity.models.showroom import DailySale, Customer, ShowRoom, Month


@dataclass
class MergedProduct:
    code: str
    p_C: Product
    p_I: Product
    p_O: Product


if __name__ == "__main__":
    pass
