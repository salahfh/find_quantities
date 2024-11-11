import logging
from collections import defaultdict
from dataclasses import dataclass, field

import pulp

logger = logging.getLogger(__name__)


class ProductAlreadyAdded(Exception):
    """When trying to add the same product more than once, it'll alert you."""

    pass


@dataclass(frozen=True)
class Product:
    """A product from the inventory"""

    n_article: str
    designation: str
    groupe_code: str
    stock_qt: int
    prix: float
    max_sales_precentage_from_total_sales: float = 0


@dataclass
class Sale:
    '''Class to hold final data returned after calculating the quantities.'''
    product: Product
    units_sold: int = 0

    @property
    def sale_total_amount(self):
        return self.product.prix * self.units_sold


@dataclass
class ShowRoom:
    refrence: str
    assigned_total_sales: float
    sales: list[Sale] = field(default_factory=list)

    def __str__(self):
        return f"Showroom {self.refrence}"

    def __repr__(self):
        return self.__str__()

    def add_sale(self, product: Product) -> None:
        self.sales.append(product)



@dataclass
class Var:
    '''Class to simplifing working with the solver and storing its data.'''
    product: Product
    showroom: ShowRoom
    variable_name: str
    variable_obj: pulp.LpVariable
    sales_formula = None


class Variables:
    def __init__(self) -> None:
        self.vars: list[Var] = []
    
    def __iter__(self):
        return iter(self.vars)
    
    def add_variable(self, var: Var) -> None:
        self.vars.append(var)

    def get_max_product_total_sale_per_showroom(self, var: Var) -> float:
        return var.product.max_sales_precentage_from_total_sales * \
                var.showroom.assigned_total_sales
    
    def get_formula_for_sales_per_showroom(self, sh: ShowRoom) -> pulp.LpConstraint:
        d = defaultdict(pulp.LpConstraint)
        for var in self.vars:
            d[var.showroom.refrence] += var.sales_formula 
        return d[sh.refrence]
    


class Solver:
    def __init__(self) -> None:
        self.products: set[Product] = set()
        self.showrooms: list[ShowRoom] = list()
        self.feasable_status: bool = None
        self.solver_options = {'keepFiles': 0,
                          'mip': True,
                          'msg': False,
                          'options': [],
                          'solver': 'PULP_CBC_CMD',
                          'timeLimit': None,
                          'warmStart': False}

    def add_product(self, product: Product) -> None:
        if product not in self.products:
            self.products.add(product)

    def add_showroom(self, showroom: ShowRoom) -> None:
        if showroom not in self.showrooms:
            self.showrooms.append(showroom)

    def is_solution_feasable(self) -> bool | None:
        if self.feasable_status is None:
            return None
        if self.feasable_status == 1:
            return True
        return False

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
        solver = pulp.getSolverFromDict(self.solver_options)
        prob = pulp.LpProblem("FindQuantities", pulp.LpMinimize)

        # Variables Qi?
        decision_variables = Variables()
        for sh in self.showrooms:
            for p in self.products:
                variable_name = f"q_{sh.refrence}_{p.n_article}"
                variable = pulp.LpVariable(
                    variable_name, lowBound=0, upBound=p.stock_qt, cat='Integer'
                )
                v = Var(
                        variable_name=variable_name.replace('-', '_'),
                        product=p,
                        showroom=sh,
                        variable_obj=variable
                        )
                decision_variables.add_variable(v)

        for v in decision_variables:
            v.sales_formula = v.variable_obj * v.product.prix
        formulas = sum(v.sales_formula for v in decision_variables)
        prob += formulas

        # Objective
        all_showrooms_sales = sum((sh.assigned_total_sales for sh in self.showrooms))
        prob += formulas == all_showrooms_sales, "total_sale_matches"

        # Constaints
        # 1. respect percentage of total sales
        for v in decision_variables:
            prob += v.sales_formula <= decision_variables.get_max_product_total_sale_per_showroom(v),\
                f'{v.variable_name} total sales must <= {decision_variables.get_max_product_total_sale_per_showroom(v)}'

        # 2. Total sales for the showroom should still match
        for sh in self.showrooms:
            prob += decision_variables.get_formula_for_sales_per_showroom(sh) == sh.assigned_total_sales

        # print(prob)
        self.feasable_status = prob.solve(solver)
        for solution in prob.variables():
            # logger.debug(f"Solution: {v.name} = {v.varValue}")
            quantity = solution.varValue
            for v in decision_variables:
                if solution.name == v.variable_name:
                    sale = Sale(product=v.product, units_sold=int(quantity))
                    v.showroom.add_sale(sale)
                    break


if __name__ == "__main__":

    sh1 = ShowRoom(refrence="sh-bba", assigned_total_sales=1050)
    sh2 = ShowRoom(refrence="sh-alger", assigned_total_sales=200)

    p1 = Product(
        designation=f"p{1}",
        n_article=f"Product_{1}",
        stock_qt=1000,
        groupe_code='P1',
        prix=1,
        max_sales_precentage_from_total_sales=.31
    )
    p2 = Product(
        designation=f"p{2}",
        n_article=f"Product_{2}",
        stock_qt=1000,
        groupe_code='P1',
        prix=2,
        max_sales_precentage_from_total_sales=.2
    )
    p3 = Product(
        designation=f"p{3}",
        n_article=f"Product_{3}",
        stock_qt=5000,
        groupe_code='P1',
        prix=3.3,
        max_sales_precentage_from_total_sales=.6
    )
    p4 = Product(
        designation=f"p{4}",
        n_article=f"Product_{4}",
        stock_qt=5000,
        groupe_code='P2',
        prix=.3,
        max_sales_precentage_from_total_sales=.3
    )

    solver = Solver()

    for p in [p1, p2, p3, p4]:
        solver.add_product(p)
    for sh in [sh1, sh2]:
        solver.add_showroom(sh)
    solver.calculate_quantities()
    for sh in [sh1, sh2]:
        print(f'{sh.refrence}: total sales: {sum((s.sale_total_amount for s in sh.sales))}')
        for sale in sh.sales:
            print(f'\tQuantity: {sale.units_sold} x Price: {sale.product.prix} = {sale.sale_total_amount}')
    print(solver.is_solution_feasable())
