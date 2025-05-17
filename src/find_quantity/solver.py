import math
import random
from typing import Callable
from collections import defaultdict
from dataclasses import dataclass
from functools import partialmethod

from find_quantity.models import Package, Inventory, Sale, ShowRoom



def generate_equal_qt(sample_length: int, quantity_to_divide: int) -> list[int]:
    """
    Generate a list of quantities in shuffled order.
    """
    q, r = divmod(quantity_to_divide, sample_length)
    qt = [q for _ in range(sample_length)]
    for i in range(len(qt)):
        r -= 1
        if r < 0:
            break
        qt[i] += 1
    random.shuffle(qt)
    return qt


def generate_random_qt(
    sample_length: int, quantity_to_divide: int
) -> list[int]:
    """
    Generate a list of random quantities in shuffled order.

    URL: https://www.reddit.com/r/learnpython/comments/cpwxpe/generate_n_random_integers_which_all_add_up_to_a/
    """
    rand_n = [random.random() for i in range(sample_length)]
    result = [math.floor(i * quantity_to_divide / sum(rand_n)) for i in rand_n]
    # randomly add missing numbers
    for _ in range(quantity_to_divide - sum(result)):
        result[random.randint(0, sample_length-1)] += 1
    return result


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
            for p in packages:
                max_product = self.determine_max_product(product_percentage, p)
                for q in range(max_product, 0, -1):
                    total = q * p.prix
                    if (difference - total) >= 0:
                        difference -= total
                        sales += inventory.record_sale(package=p, qt=q)
                        break
                if difference <= 0:
                    notsolved = False
                    break
            if len(packages) == 0 or attempts < 0:
                break
            attempts -= 1
            product_percentage += 0.001
        return sales

    distribute_products_by_showroom = partialmethod(
        distrubute_maximum_of_all_products, product_percentage=0.01, attempts=100
    )

    distribute_products_monthly = partialmethod(
        distrubute_maximum_of_all_products, product_percentage=1, attempts=100
    )

    def determine_max_product(self, product_percentage: float, p: Package):
        max_product = int(p.stock_qt * product_percentage)
        max_product = min(p.stock_qt, max_product) if max_product > 0 else p.stock_qt
        return max_product

    def allocate_remaining_products(self, inventory: Inventory) -> list[Sale]:
        """
        Distribute remaining products/packages so all product will be used.
        """
        packages = inventory.get_packages()
        sales = []
        for p in packages:
            sales += inventory.record_sale(qt=p.stock_qt, package=p)
        return sales

    def distrubute_products(
        self,
        inventory: Inventory,
        n: int,
        quantity_distributor: Callable
    ) -> list[list[Sale]]:
        """
        Distrute packages equally on N customers. Also it shuffles them before generating the sales.
        It purpose to make it look credible that products are distrubted in a randomized manner.
        """
        sales = defaultdict(list)
        packages = inventory.get_packages()
        packages = random.sample(packages, k=len(packages))
        for p in packages:
            eqaul_qt_list = [(p, q) for q in quantity_distributor(n, p.stock_qt)]
            sales_list_packaged = [inventory.record_sale(package=p, qt=q) for p, q in eqaul_qt_list]
            for i, s in enumerate(sales_list_packaged):
                sales[i] += s
        return sales.values()

    distrubute_products_equally = partialmethod(
        distrubute_products, quantity_distributor=generate_equal_qt
    )

    distrubute_products_randomly = partialmethod(
        distrubute_products, quantity_distributor=generate_random_qt
    )

if __name__ == "__main__":
    pass
