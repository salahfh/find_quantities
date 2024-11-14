from dataclasses import dataclass
from find_quantity.model import ShowRoom, Product, Sale
from find_quantity.debug import timer

import pulp

SOLVER_TIME_LIMIT = 240
SOLVER_ACCURACY_LIMIT = 0.001   # is it doing anything?


@dataclass
class Var:
    '''Class to simplifing working with the solver and storing its data.'''
    product: Product
    showroom: ShowRoom
    variable_name: str
    variable_obj: pulp.LpVariable
    sales_formula = None

    @staticmethod
    def frmt_var_name(name: str) -> str:
        for char in [' ', '-', '.']:
            name = name.replace(char, '_')
        return name


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


@dataclass
class Metrics:
    showroom: ShowRoom
    tolerance: float
    solver_optimal: float
    solver_status: int
    solver_status_str: str

    @property
    def s_calc(self):
        return self.showroom.calculated_total_sales

    @property
    def s_assigned(self):
        return self.showroom.assigned_total_sales

    @property
    def limit(self) -> float:
        return self.tolerance * self.s_assigned

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
        return len([s for s in self.showroom.sales if s.units_sold > 0])


class Solver:
    def __init__(self, tolerance=0) -> None:
        self.tolerence: float = tolerance
        self.products: list[Product] = list()
        self.showroom: ShowRoom
        self.metrics: Metrics = None

    @property
    def limit(self) -> int:
        return self.showroom.assigned_total_sales * self.tolerence

    def add_products(self, products: list[Product]) -> None:
        for product in products:
            if product not in self.products:
                self.products.append(product)

    def add_showroom(self, showroom: ShowRoom) -> None:
        self.showroom = showroom

    def is_it_solved_correctly(self):
        calc = self.showroom.calculated_total_sales
        assigned = self.showroom.assigned_total_sales
        return (assigned - self.limit) <= calc <= (assigned + self.limit)

    @timer
    def calculate_quantities(self) -> None:
        '''
        Calculate the quantities required for each product.

        Solves this equation: T = SUM(Qi *Pi) + Epi
        T: Total Assigned 
        Qi: Quantity of item i
        Pi: Price of item i
        Epi: Error tolereance

        Selection Considerations:
        1. Picks items only with stock
        2. Tries to honor the totals max percentage 
        '''
        solver = pulp.PULP_CBC_CMD(
            msg=False,
            timeLimit=SOLVER_TIME_LIMIT,
            gapRel=SOLVER_ACCURACY_LIMIT,
        )
        prob = pulp.LpProblem("FindQuantities", pulp.LpMaximize)

        # Variables Qi?
        decision_variables = Variables()
        for p in self.products:
            variable_name = f"q_{p.n_article}"
            variable = pulp.LpVariable(
                variable_name, lowBound=0, upBound=p.stock_qt, cat='Integer'
            )
            v = Var(
                variable_name=Var.frmt_var_name(variable_name),
                product=p,
                showroom=self.showroom,
                variable_obj=variable
            )
            decision_variables.add_variable(v)

        for v in decision_variables:
            v.sales_formula = v.variable_obj * v.product.prix
        formulas = sum(v.sales_formula for v in decision_variables)
        prob += formulas

        # Objective
        prob += formulas, 'Total Sales Match'

        # Constaints
        # 1. respect percentage of total sales
        for v in decision_variables:
            prob += v.sales_formula <= decision_variables.get_max_product_total_sale_per_showroom(v), \
                f'{v.variable_name} total sales must <= {
                    decision_variables.get_max_product_total_sale_per_showroom(v)}'

        upper_bound = self.showroom.assigned_total_sales + self.limit
        lower_bound = self.showroom.assigned_total_sales - self.limit
        prob += formulas <= upper_bound
        prob += formulas >= lower_bound

        # Solving the problem
        prob.solve(solver)

        # Processing solution
        for solution in prob.variables():
            quantity = solution.varValue
            for v in decision_variables:
                if solution.name == v.variable_name:
                    sale = Sale(product=v.product, units_sold=int(quantity))
                    v.showroom.add_sale(sale)
                    break

        self.metrics = Metrics(
            showroom=self.showroom,
            tolerance=self.tolerence,
            solver_optimal=prob.objective.value(),
            solver_status=prob.status,
            solver_status_str=pulp.LpStatus[prob.status],
        )


if __name__ == '__main__':
    pass
