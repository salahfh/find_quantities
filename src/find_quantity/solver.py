import random
from collections import defaultdict
from dataclasses import dataclass
from functools import partialmethod

from find_quantity.model import Inventory, Product, Sale, ShowRoom


@dataclass
class Metrics:
    showroom: ShowRoom

    @property
    def s_calc(self):
        return self.showroom.calculated_total_sales

    @property
    def s_assigned(self):
        return self.showroom.assigned_total_sales

    @property
    def difference(self) -> float:
        return abs(self.s_assigned - self.s_calc)

    @property
    def ratio(self) -> float:
        if self.s_assigned == 0:
            return 0
        return round(self.difference / self.s_assigned, 2)

    @property
    def num_products_used(self) -> int:
        return len(set([s.product for s in self.showroom.sales if s.units_sold > 0]))


class Solver:
    def distrubute_maximum_of_all_products(
        self,
        inventory: Inventory,
        target_amount: float,
        product_percentage: float = 1,
        attempts: int = 2,
    ) -> list[Sale]:
        difference = target_amount
        notsolved = True
        sales = []
        while notsolved:
            packages = inventory.get_packages()
            product_percentage += 0.001
            for p in packages:
                max_product = self.determine_max_product(product_percentage, p)
                for q in range(max_product, 0, -1):
                    total = q * p.prix
                    if (difference - total) >= 0:
                        difference -= total
                        s = inventory.record_sale(package=p, qt=q)
                        sales += s
                        break
                if difference <= 0:
                    notsolved = False
                    break
            if len(packages) == 0 or attempts < 0:
                break
            attempts -= 1
        return sales

    distribute_products_by_showroom = partialmethod(
        distrubute_maximum_of_all_products, product_percentage=0.1, attempts=100
    )

    distribute_products_monthly = partialmethod(distrubute_maximum_of_all_products)

    def determine_max_product(self, product_percentage: float, p: Product):
        max_product = int(p.stock_qt * product_percentage)
        max_product = min(p.stock_qt, max_product) if max_product > 0 else p.stock_qt
        return max_product

    def allocate_remaining_products(self, inventory: Inventory) -> list[Sale]:
        products = inventory.get_products()
        sales = []
        for p in products:
            s = Sale(product=p, units_sold=p.stock_qt)
            sales.append(s)
        inventory.update_quantities(sales=sales)
        return sales

    def generate_equal_qt(self, n: int, summ: int) -> list[int]:
        q, r = divmod(summ, n)
        qt = [q for _ in range(n)]
        for i in range(len(qt)):
            r -= 1
            if r < 0:
                break
            qt[i] += 1
        # random.shuffle(qt)
        return qt

    def distrubute_products_equally(
        self, inventory: Inventory, n: int
    ) -> list[list[Sale]]:
        products = inventory.get_packages()
        sales = defaultdict(list)
        for p in products:
            sl = [
                inventory.record_sale(package=p, qt=q)
                for q in self.generate_equal_qt(n=n, summ=p.stock_qt)
            ]
            for i, s in enumerate(sl):
                sales[i] += s
        return sales.values()


if __name__ == "__main__":
    pass
