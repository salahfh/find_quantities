from pathlib import Path
from find_quantity.model import ShowRoom, Product, MergedProduct
from find_quantity.data_quality_control import ValidateProductQuantity
from find_quantity.solver import Metrics
from find_quantity.commons import IOTools


class Report:
    def __init__(self,
                 output_folder: Path = Path('data/output/')
                 ) -> None:
        self.skip_zero_quantities: bool = True
        self.output_folder = output_folder

    @IOTools.to_csv(mode='a')
    def write_showrooms_report(self, showroom: ShowRoom, month: int, filename_prefix: str=None):
        path = self.output_folder / 'showrooms_calculation_report.csv'
        if filename_prefix:
            path = self.output_folder / f'showrooms_calculation_report_{filename_prefix}.csv'
        header = ['mois', 'Showroom', 'Assigned Sales',
                   'Quantite', 'N-Article', 'Designation',
                  'Groupe-Code', 'Prix', 'Current_Stock', 'Initial_stock' , 'Total']
        data = [(
                month,
                showroom.refrence,
                showroom.assigned_total_sales,
                s.units_sold,
                s.product.n_article,
                s.product.designation,
                s.product.groupe_code,
                s.product.prix,
                s.product.stock_qt,
                s.product.stock_qt_intial,
                s.sale_total_amount,
                ) for s in showroom.sales if s.units_sold]
        return path, header, data

    @IOTools.to_csv(mode='a')
    def write_product_transformed(self, products: list[Product], month: int, filename_prefix: str=None):
        path = self.output_folder / 'products_transformed.csv'
        if filename_prefix:
            path = self.output_folder / f'products_transformed_{filename_prefix}.csv'
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
        return path, header, data

    @IOTools.to_csv(mode='a')
    def write_showroom_transformed(self, showrooms: list[ShowRoom], month: int):
        path = self.output_folder / 'showrooms_transformed.csv'
        header = ['mois', 'refrence', 'assigned_total_sales']
        data = [
            (
                month,
                s.refrence,
                s.assigned_total_sales
            ) for s in showrooms]
        return path, header, data

    @IOTools.to_csv(mode='a')
    def write_metrics(self, metrics: Metrics, month: int):
        path = self.output_folder / 'calculation_metrics.csv'
        header = ['mois', 'refrence', 'assigned_total_sales',
                  'calculated_total', 'difference', 'diffrence_ratio',
                  'products_used']
        data = [
            (
                month,
                metrics.showroom.refrence,
                metrics.s_assigned,
                metrics.s_calc,
                metrics.difference,
                metrics.ratio,
                metrics.num_products_used,
            )]
        return path, header, data

    @IOTools.to_csv(mode='w')
    def write_merged_products(self, month: int, merged_products: list[MergedProduct]) -> None:
        path = self.output_folder / 'merged_product.csv'
        header = ['mois', 'code', 'p1_n_article', 'p1_designation', 'p1_prix',
                  'p2_n_article', 'p2_designation', 'p2_prix', ]
        data = [
            (
                month,
                ps.code,
                ps.p_I.n_article,
                ps.p_I.designation,
                ps.p_I.prix,
                ps.p_O.n_article,
                ps.p_O.designation,
                ps.p_O.prix,
            ) for ps in merged_products]
        return path, header, data

    @IOTools.to_csv(mode='w')
    def valid_product_quantity_report(self, validation_data: list[ValidateProductQuantity]) -> None:
        path = self.output_folder / 'product_quantity_validation.csv'
        header = ['mois',
                  'Product_name', 
                  'Remaining_stock',
                  'Units_sold',
                  'Raw_data_stock_initial',
                  'Stock_diff', 
                  'Calculation_correct?',
                 ]
        data = [(
                v.month,
                v.product_name,
                v.calc_stock_qt,
                v.calc_all_units_sold,
                v.calc_stock_diff,
                v.raw_data_stock_initial,
                v.is_calc_correct,
            ) for v in validation_data]
        return path, header, data

    @IOTools.to_csv(mode='a')
    def write_daily_sales(self, month: int, showroom: ShowRoom) -> None:
        path = self.output_folder / 'daily_sales.csv'
        header = ['mois',
                  'showroom', 
                  'day',
                  'n_article',
                  'designation',
                  'groupe_code', 
                  'prix', 
                  'Units_sold',
                  'Total',
                 ]
        data = [(
                month,
                showroom.refrence,
                d.day,
                s.product.n_article,
                s.product.designation,
                s.product.groupe_code,
                s.product.prix,
                s.units_sold,
                s.sale_total_amount
            ) for d in showroom.daily_sales for s in d.sales if s.units_sold]
        return path, header, data
