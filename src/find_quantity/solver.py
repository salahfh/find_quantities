from dataclasses import dataclass
from find_quantity.model import ShowRoom, Product, Sale
from find_quantity.debug import timer

import pulp

SOLVER_TIME_LIMIT = 240
SOLVER_ACCURACY_LIMIT = 0.001


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
    
    # def get_formula_for_sales_per_showroom(self, sh: ShowRoom) -> pulp.LpConstraint:
    #     d = defaultdict(pulp.LpConstraint)
    #     for var in self.vars:
    #         d[var.showroom.refrence] += var.sales_formula 
    #     return d[sh.refrence]
    


class Solver:
    def __init__(self) -> None:
        self.products: list[Product] = list()
        self.showroom: ShowRoom
        self.feasable_status: bool = None
        self.solver_options = {
            'keepFiles': 0,
            'mip': True,
            'msg': False,
            'options': [],
            'solver': 'PULP_CBC_CMD',
            'timeLimit': SOLVER_TIME_LIMIT,
            'warmStart': False,
        }

    def add_products(self, products: list[Product]) -> None:
        for product in products:
            if product not in self.products:
                self.products.append(product)

    def add_showroom(self, showroom: ShowRoom) -> None:
        self.showroom = showroom

    def is_solution_feasable(self) -> bool | None:
        if self.feasable_status is None:
            return None
        if self.feasable_status == 1:
            return True
        return False

    @timer
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
        solver = pulp.PULP_CBC_CMD(
            msg=False,
            timeLimit=SOLVER_TIME_LIMIT,
            gapRel=SOLVER_ACCURACY_LIMIT,
            )
        # solver = pulp.PULP_CBC_CMD(timeLimit=SOLVER_TIME_LIMIT, msg=False, gapRel=SOLVER_ACCURACY_LIMIT)
        prob = pulp.LpProblem("FindQuantities", pulp.LpMaximize)

        # Variables Qi?
        decision_variables = Variables()
        # for sh in self.showrooms:
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
        prob += formulas == self.showroom.assigned_total_sales , "total_sale_matches"

        # Constaints
        # 1. respect percentage of total sales
        for v in decision_variables:
            prob += v.sales_formula <= decision_variables.get_max_product_total_sale_per_showroom(v),\
                f'{v.variable_name} total sales must <= {decision_variables.get_max_product_total_sale_per_showroom(v)}'

        # Solving the problem 
        self.feasable_status = prob.solve(solver)

        # Debugging
        # print(prob)
        print('***')
        print(f"status: {prob.status}, {pulp.LpStatus[prob.status]}")
        print(f"objective: {prob.objective.value()}")
        print('***')

        # Processing solution
        for solution in prob.variables():
            # logger.debug(f"Solution: {v.name} = {v.varValue}")
            quantity = solution.varValue
            # print(f"Solution: {solution.name} = {quantity}")
            for v in decision_variables:
                if solution.name == v.variable_name:
                    sale = Sale(product=v.product, units_sold=int(quantity))
                    v.showroom.add_sale(sale)
                    break


if __name__ == '__main__':
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

    solver.add_products([p1, p2, p3, p4])
    for sh in [sh1, sh2]:
        solver.add_showroom(sh)
    solver.calculate_quantities()
    for sh in [sh1, sh2]:
        print(f'{sh.refrence}: total sales: {sum((s.sale_total_amount for s in sh.sales))}')
        for sale in sh.sales:
            print(f'\tQuantity: {sale.units_sold} x Price: {sale.product.prix} = {sale.sale_total_amount}')
    print(solver.is_solution_feasable())