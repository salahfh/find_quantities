import csv
from find_quantity.model import ShowRoom


class Report:
    def __init__(self, month: int, showroom: ShowRoom) -> None:
        self.showroom = showroom
        self.month = month    
    
    def write_csv_report(self):
        filename = f'data/output/{self.month}/{self.showroom.refrence}.csv'.replace(' ', '_')
        header = ['N-Article', 'Designation', 'Groupe-Code', 'Prix', 'Quantite', 'Total']
        with open(filename, 'w') as f:
            writer = csv.writer(f, delimiter=',', lineterminator="\n")
            writer.writerow(header)
            for s in self.showroom.sales:
                writer.writerow([
                    s.product.n_article,
                    s.product.designation, 
                    s.product.groupe_code,
                    s.product.prix,
                    s.units_sold,
                    s.sale_total_amount
                ])
