from typing import Literal
from functools import wraps
from pathlib import Path
import csv
from find_quantity.model import ShowRoom, Product
from find_quantity.solver import Metrics


class Report:
    def __init__(self,
                 auto_write=True,
                 output_folder: Path = Path(f'data/output/')
                 ) -> None:
        self.output_folder: Path = output_folder
        self.showrooms: list[tuple[int, ShowRoom]] = []
        self.auto_write: bool = auto_write
        self.skip_zero_quantities: bool = True
        # self._cleanup()

    def _cleanup(self):
        for f in self.output_folder.glob('*.csv'):
            f.unlink()

    def add_showroom(self, month: int, showroom: ShowRoom) -> None:
        if not self.auto_write:
            self.showrooms.append(month, showroom)
        else:
            self.write_showrooms_report(showroom=showroom, month=month)

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
                    if writer_header:
                        writer.writerow(header)
                    for line in data:
                        writer.writerow(line)
            return wrapper
        return decorated

    @to_csv(mode='a')
    def write_showrooms_report(self, showroom: ShowRoom, month: int):
        header = ['Showroom', 'N-Article', 'Designation',
                  'Groupe-Code', 'Prix', 'Quantite', 'Total']
        filename = f'month_{month}.csv'
        data = [(
                showroom.refrence,
                s.product.n_article,
                s.product.designation,
                s.product.groupe_code,
                s.product.prix,
                s.units_sold,
                s.sale_total_amount,
                ) for s in showroom.sales]
        return filename, header, data

    @to_csv(mode='w')
    def write_product_obj(self, filename: Path, products: list[Product]):
        header = ['n_article', 'designation',
                  'groupe_code', 'prix', 'stock_qt']
        data = [
            (
                p.n_article,
                p.designation,
                p.groupe_code,
                p.prix,
                p.stock_qt,
            ) for p in products]
        return filename, header, data

    @to_csv(mode='w')
    def write_showroom_obj(self, filename: Path, showrooms: list[ShowRoom]):
        header = ['refrence', 'assigned_total_sales']
        data = [
            (
                s.refrence,
                s.assigned_total_sales
            ) for s in showrooms]
        return filename, header, data

    @to_csv(mode='a')
    def write_metrics(self, filename: Path, metrics: Metrics):
        header = ['refrence', 'assigned_total_sales',
                  'calculated_total', 'difference', 'diffrence_ratio',
                  'difference_limit', 'tolerance', 'solver_status',
                  'products_used']
        data = [
            (
                metrics.showroom.refrence,
                metrics.s_assigned,
                metrics.s_calc,
                metrics.difference,
                metrics.ratio,
                metrics.limit,
                metrics.tolerance,
                metrics.solver_status_str,
                metrics.num_products_used
            )]
        return filename, header, data
