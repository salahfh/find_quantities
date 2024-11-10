import logging
from dataclasses import dataclass, field

import pulp

logger = logging.getLogger(__name__)


class ProductAlreadyAdded(Exception):
    """When trying to add the same product more than once, it'll alert you."""

    pass


@dataclass(frozen=True)
class Product:
    """A product from the inventory"""

    refrence: str
    name: str
    stock_qt: int
    price: float
    taxable: bool = False
    max_sales_precentage_from_total_sales: float = 0


@dataclass
class Sale:
    '''Class to hold final data returned after calculating the quantities.'''
    product: Product
    units_sold: int = 0

    @property
    def sale_total_amount(self):
        return self.product.price * self.units_sold


@dataclass
class Var:
    '''Class to simplifing working with the solver and storing its data.'''
    product: Product
    variable_name: str
    variable_obj: pulp.LpVariable
    sales_formula = None


@dataclass
class ShowRoom:
    refrence: str
    location: str
    assigned_total_sales: float
    products: set[Product] = field(default_factory=set)
    sales: list[Sale] = field(default_factory=list)
    feasable_status: bool = None

    def is_solution_feasable(self) -> bool|None:
        if self.feasable_status is None:
            return None
        if self.feasable_status == 1:
            return True
        return False


    def log_message(self, message) -> None:
        logger.debug(f"{self}: {message}")

    def add_product(self, product: Product) -> None:
        if product not in self.products:
            self.products.add(product)
        else:
            self.log_message(
                f"Product already added: Skipping. {product.name}")
            raise ProductAlreadyAdded

    def calculate_quantities(self) -> None:
        '''
        Calculate the quantities required for each product.

        Solves this equation: T = SUM(Qi *Pi)
        T: Total Assigned 
        Qi: Quantity of item i
        Pi: Price of item i

        Selection Considerations:
        1. Picks items only with stock
        2. Tries to honor the totals max percentage 
        3. Sets the feasable_status after calculation
        '''
        solver_options = {'keepFiles': 0,
                          'mip': True,
                          'msg': False,
                          'options': [],
                          'solver': 'PULP_CBC_CMD',
                          'timeLimit': None,
                          'warmStart': False}
        solver = pulp.getSolverFromDict(solver_options)

        prob = pulp.LpProblem("FindQuantities", pulp.LpMinimize)

        # Variables Qi?
        decision_variables: list[Var] = []
        for p in self.products:
            variable_name = f"q_{p.name}"
            variable = pulp.LpVariable(
                variable_name, lowBound=0, upBound=p.stock_qt, cat='Integer'
            )
            v = Var(product=p, variable_name=variable_name,
                    variable_obj=variable)
            decision_variables.append(v)

        # Objective
        for v in decision_variables:
            v.sales_formula = v.variable_obj * v.product.price
        formulas = sum(v.sales_formula for v in decision_variables)
        prob += formulas

        # Constaints
        prob += formulas == self.assigned_total_sales, "total_sale_matches"
        for v in decision_variables:
            # respect percentage of total sales
            product_total_sales = v.product.max_sales_precentage_from_total_sales * \
                self.assigned_total_sales
            prob += v.sales_formula <= product_total_sales, f'{
                v.product.name} total sales must <= {product_total_sales}'

        # print(prob)
        self.feasable_status = prob.solve(solver)
        for v in prob.variables():
            logger.debug(f"Solution: {v.name} = {v.varValue}")
            for p in decision_variables:
                if v.name == p.variable_name:
                    self.sales.append(Sale(product=p.product, units_sold=int(v.varValue)))

    def balance_sales(self) -> None:
        """

        R: Reminder
        T: Total Assigned Sales
        Qi: Quantity of an item i
        Qj: a 2nd Quantity of an Quantity i
        Pi: Price of an item i
        Eps: Epsilion - Margin of error allowed
        1. R = T - SUM(Qi * Pi) + Eps
        """


    def __str__(self):
        return f"Showroom {self.refrence}"

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":

    sh = ShowRoom(refrence="sh1", location="bba", assigned_total_sales=1000)

    p1 = Product(
        refrence=f"p{1}",
        name=f"Product_{1}",
        stock_qt=1000,
        price=1,
        max_sales_precentage_from_total_sales=.31
    )
    p2 = Product(
        refrence=f"p{2}",
        name=f"Product_{2}",
        stock_qt=1000,
        price=2,
        max_sales_precentage_from_total_sales=.2
    )
    p3 = Product(
        refrence=f"p{3}",
        name=f"Product_{3}",
        stock_qt=5000,
        price=3.3,
        max_sales_precentage_from_total_sales=.6
    )
    for p in [p1, p2, p3]:
        sh.add_product(p)
    sh.calculate_quantities()
    for sale in sh.sales:
        print('Quantity: ', sale.units_sold, sale.sale_total_amount)
    print('Total Stales: ', sum((s.sale_total_amount for s in sh.sales)))
    print(sh.is_solution_feasable())
