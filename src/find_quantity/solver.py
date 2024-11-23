from dataclasses import dataclass
from find_quantity.model import ShowRoom, Sale, Inventory



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
    def manually_find_closests_match(self,
                                     inventory: Inventory,
                                     showroom: ShowRoom,
                                     product_percentage: float = 1,
                                     attempts: int = 2
                                     ) -> ShowRoom:
        difference = showroom.assigned_total_sales 
        notsolved = True
        while notsolved:
            sales = []
            products = inventory.get_products()
            product_percentage += .001
            for p in products:
                max_product = int(p.stock_qt * product_percentage)
                max_product = min(p.stock_qt, max_product) if max_product > 0 else p.stock_qt
                for q in range(max_product, 0, -1):
                    total = q * p.prix
                    if (difference - total) >= 0:
                        s = Sale(
                            product=p,
                            units_sold=q,
                        )
                        difference -= total
                        sales.append(s)
                        showroom.add_sale(s)
                        break
                if difference <= 0:
                    notsolved = False
                    break
            if len(products) == 0 or attempts < 0:
                break
            inventory.update_quantities(sales=sales)
            attempts -= 1
        return showroom


if __name__ == '__main__':
    pass
