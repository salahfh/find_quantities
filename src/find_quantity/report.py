from pathlib import Path
import csv
from find_quantity.model import ShowRoom, Product


class Report:
    def __init__(self, auto_write=True) -> None:
        self.output_folder: Path = Path(f'data/output/')
        self.showrooms: list[tuple[int, ShowRoom]] = []
        self.auto_write: bool = auto_write
        self.skip_zero_quantities: bool = True
        self._cleanup()

    def _cleanup(self):
        for f in self.output_folder.glob('*.csv'):
            f.unlink()

    def add_showroom(self, month: int, showroom: ShowRoom) -> None:
        if not self.auto_write:
            self.showrooms.append(month, showroom)
        else:
            self.write_showrooms_report(showroom=showroom, month=month)

    def write_showrooms_report(self, showroom: ShowRoom, month: int):
        header = ['Showroom', 'N-Article', 'Designation', 'Groupe-Code', 'Prix', 'Quantite', 'Total', 'Correct?']
        filename = self.output_folder / f'month_{month}.csv'
        write_header = False
        if not filename.exists():
            write_header = True

        with open(filename, 'a') as f:
            writer = csv.writer(f, delimiter=',', lineterminator="\n")
            if write_header:
                writer.writerow(header)
            for s in showroom.sales:
                if s.units_sold == 0:
                    continue
                writer.writerow([
                    showroom.refrence,
                    s.product.n_article,
                    s.product.designation, 
                    s.product.groupe_code,
                    s.product.prix,
                    s.units_sold,
                    s.sale_total_amount, 
                    showroom.was_calculation_correct()
                ])
    
    def write_remaining_products_report(self, products: list[Product]):
        with open('data/output/product.csv', 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(
                (['Article', 'Initial Quantity', 'Current', 'used']),)
            for p in products:
                writer.writerow(
                    (
                        p.n_article,
                        p.stock_qt_intial,
                        p.stock_qt,
                        p.stock_qt_intial - p.stock_qt
                    ),
                )
