from typing import Literal
from functools import wraps
from pathlib import Path
import csv
from find_quantity.model import ShowRoom, Product
from find_quantity.solver import Metrics


class Report:
    def __init__(self,
                 output_folder: Path = Path(f'data/output/')
                 ) -> None:
        self.output_folder: Path = output_folder
        self.skip_zero_quantities: bool = True

    def _cleanup(self):
        for f in self.output_folder.glob('*.csv'):
            f.unlink()

    def to_csv(mode: Literal['a', 'w']):
        '''Define a wrapper for to_csv'''
        def decorated(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                filename, header, data = func(self, *args, **kwargs)
                path = Path(self.output_folder / filename)
                writer_header = True if not path.exists() else False
                with open(path, mode) as f:
                    writer = csv.writer(f, lineterminator='\n')
                    if writer_header or mode == 'w':
                        writer.writerow(header)
                    for line in data:
                        writer.writerow(line)
            return wrapper
        return decorated

    @to_csv(mode='a')
    def write_showrooms_report(self, showroom: ShowRoom, month: int):
        filename = f'month_{month}.csv'
        header = ['mois', 'Showroom', 'N-Article', 'Designation',
                  'Groupe-Code', 'Prix', 'Quantite', 'Total']
        data = [(
                month,
                showroom.refrence,
                s.product.n_article,
                s.product.designation,
                s.product.groupe_code,
                s.product.prix,
                s.units_sold,
                s.sale_total_amount,
                ) for s in showroom.sales if s.units_sold > 0]
        return filename, header, data

    @to_csv(mode='w')
    def write_product_obj(self, products: list[Product], month: int):
        filename=f'products_transformed_{month}.csv'
        header = ['mois', 'n_article', 'designation',
                  'groupe_code', 'prix', 'stock_qt', 'intial_stock_qt']
        data = [
            (
                month,
                p.n_article,
                p.designation,
                p.groupe_code,
                p.prix,
                p.stock_qt,
                p.stock_qt_intial
            ) for p in products]
        return filename, header, data

    @to_csv(mode='w')
    def write_showroom_obj(self, showrooms: list[ShowRoom], month: int):
        filename=f'showrooms_transformed_{month}.csv'
        header = ['mois', 'refrence', 'assigned_total_sales']
        data = [
            (
                month,
                s.refrence,
                s.assigned_total_sales
            ) for s in showrooms]
        return filename, header, data

    @to_csv(mode='a')
    def write_metrics(self, metrics: Metrics, month: int):
        filename=f'metrics_{ month}.csv'
        header = ['mois', 'refrence', 'assigned_total_sales',
                  'calculated_total', 'difference', 'diffrence_ratio',
                  'difference_limit', 'tolerance', 'solver_status',
                  'products_used', 'max_product_sales_percentage']
        data = [
            (
                month,
                metrics.showroom.refrence,
                metrics.s_assigned,
                metrics.s_calc,
                metrics.difference,
                metrics.ratio,
                metrics.limit,
                metrics.tolerance,
                metrics.solver_status_str,
                metrics.num_products_used,
                metrics.max_product_sales_percentage
            )]
        return filename, header, data
