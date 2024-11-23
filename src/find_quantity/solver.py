import random
import itertools
from dataclasses import dataclass
from find_quantity.model import ShowRoom, Product, Sale, Inventory, CannotCheckoutMoreThanStockQTException
from find_quantity.cache import Cache

import pulp

SOLVER_TIME_LIMIT = 20
SOLVER_ACCURACY_LIMIT = 1   # is it doing anything?
SOLVER_ERROR_TOLERANCE = [1 / 10**i for i in [9, 6, 3]]
SOLVER_PRODUCT_MAX_PERCENTAGE = [.1, .12, .15, .2, .3, .5, .7]


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

    # def get_max_product_total_sale_per_showroom(self, var: Var) -> float:
    #     return var.product.max_sales_precentage_from_total_sales * \
    #         var.showroom.assigned_total_sales


@dataclass
class Metrics:
    showroom: ShowRoom
    tolerance: float
    max_product_sales_percentage: float
    solved_correctly: bool

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
    def __init__(self, products: list[Product]=None):
        self.products = products
    
    def limit(self, showroom:ShowRoom, tolerance: float) -> int:
        return showroom.assigned_total_sales * tolerance

    def is_it_solved_correctly(self, showroom: ShowRoom, tolerance: float):
        calc = showroom.calculated_total_sales
        assigned = showroom.assigned_total_sales
        limit = self.limit(showroom, tolerance)
        # return (assigned - limit) <= calc <= (assigned + limit)
        return True

    def calculate_quantities(self,
            showroom: ShowRoom,
            tolerance: float = 1/10*9,
            max_product_sales_percentage: float=.1
        ) -> tuple[ShowRoom, Metrics]:
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
                showroom=showroom,
                variable_obj=variable
            )
            decision_variables.add_variable(v)

        for v in decision_variables:
            v.sales_formula = v.variable_obj * v.product.prix
        formulas = sum(v.sales_formula for v in decision_variables)

        # Objective
        prob += formulas, 'Total Sales Match'

        # Constaints
        # 1. respect percentage of total sales
        for v in decision_variables:
            product_usage_limit = v.product.stock_qt * max_product_sales_percentage
            prob += v.variable_obj <= product_usage_limit, \
                f'{v.variable_name} total sales must <= {product_usage_limit}'

        limit = self.limit(showroom, tolerance)
        upper_bound = showroom.assigned_total_sales + limit
        lower_bound = showroom.assigned_total_sales - limit
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

        metrics = Metrics(
            showroom=showroom,
            tolerance=tolerance,
            max_product_sales_percentage=max_product_sales_percentage,
            solved_correctly=self.is_it_solved_correctly(showroom, tolerance)
        )
        return (showroom, metrics)
    
    def manually_find_closests_match(self,
                                     inventory: Inventory,
                                     showroom: ShowRoom,
                                     product_percentage: float = 1,
                                     ) -> ShowRoom:
        difference = showroom.assigned_total_sales #- showroom.calculated_total_sales
        notsolved = True
        attempts = 2
        while notsolved:
            sales = []
            products = inventory.get_products()
            for p in products:
                max_product = p.stock_qt * product_percentage
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

                
    

class SolverRunner:
    def __init__(self,
                 inventory: Inventory,
                ):
        self.inventory = inventory
        self.products: list[Product] = list()
        self.showroom: ShowRoom
        self.tolerances = SOLVER_ERROR_TOLERANCE
        self.max_product = SOLVER_PRODUCT_MAX_PERCENTAGE
    
    def calc_monthly_quantities(self, sh: ShowRoom, month: int):
        '''
        Calculate quantity for a a given showroom after trying multiple tolerances.
        '''

        @Cache.cached(include_only_fltr=lambda x: x[1].solved_correctly)
        def calc_func(showroom, tolerence, max_product_percentage):
            '''
            Function that caches the calls. It uses metrics object to filter out.
            '''
            sh_solved, metrics = solver.calculate_quantities(showroom=showroom,
                tolerance=tolerence,
                max_product_sales_percentage=max_product_percentage)
            return sh_solved, metrics

        for tolerence, max_product_percentage in itertools.product(self.tolerances, self.max_product):
            print(f'\t{ month}/Params - tolerence: {tolerence}, product_percen: {max_product_percentage}')
            solver = Solver(products=self.inventory.get_products())
            try:
                sh_solved, metrics = calc_func(showroom=sh,
                    tolerence=tolerence,
                    max_product_percentage=max_product_percentage)
            except CannotCheckoutMoreThanStockQTException:
                print('\t Invalid Solution - Retrying without cache')
                sh_solved, metrics = solver.calculate_quantities(showroom=sh,
                    tolerance=tolerence,
                    max_product_sales_percentage=max_product_percentage)

            if metrics.solved_correctly:
                self.inventory.update_quantities(sales=sh_solved.sales)
                sh_solved = solver.manually_find_closests_match(self.inventory.get_products(), showroom=sh_solved)
                self.inventory.update_quantities(sales=sh_solved.sales)
                # sh_solved.sales = self.inventory.split_products(sales=sh_solved.sales)
                break
        return sh_solved, metrics
    
    

if __name__ == '__main__':
    pass
