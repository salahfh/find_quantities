from pathlib import Path

from find_quantity.commons import IOTools
from find_quantity.model import MergedProduct, Product, ShowRoom
from find_quantity.solver import Metrics


class Report:
    def __init__(self, output_folder: Path = Path("data/output/")) -> None:
        self.skip_zero_quantities: bool = True
        self.output_folder = output_folder
    

    @IOTools.to_csv(mode="w")
    def write_generic_list(self, path, header, data):
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_generic_list_of_dicts(
        self, ld: list[dict], filename: str, split_values: str = None
    ):
        path = self.output_folder / f"{filename}.csv"
        header = ld[0].keys()
        data = [tuple(d.values()) for d in ld]
        if split_values:
            for portion in split_values:
                chunk = [row for row in data if row[0] == portion]
                path2 = path.parents[0] / f"{path.stem}_{portion}.csv"
                self.write_generic_list(path2, header, chunk)
            data = []
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_showrooms_report(
        self, showroom: ShowRoom, month: int, filename_prefix: str = None
    ):
        path = self.output_folder / "showrooms_calculation_report.csv"
        if filename_prefix:
            path = (
                self.output_folder
                / f"showrooms_calculation_report_{filename_prefix}.csv"
            )
        header = [
            "mois",
            "Showroom",
            "Assigned Sales",
            "Quantite",
            "N-Article",
            "Designation",
            "Groupe-Code",
            "Prix",
            "RTA",
            "TEE",
            "TVA",
            "Current_Stock",
            "Initial_stock",
            "Total",
        ]
        data = [
            (
                month,
                showroom.refrence,
                showroom.assigned_total_sales,
                s.units_sold,
                s.product.n_article,
                s.product.designation,
                s.product.groupe_code,
                s.product.prix,
                s.product.rta,
                s.product.tee,
                s.product.tva,
                s.product.stock_qt,
                s.product.stock_qt_intial,
                s.sale_total_amount,
            )
            for s in showroom.sales
            if s.units_sold
        ]
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_product_transformed(
        self, products: list[Product], month: int, filename_prefix: str = None
    ):
        path = self.output_folder / "products_transformed.csv"
        if filename_prefix:
            path = self.output_folder / f"products_transformed_{filename_prefix}.csv"
        header = [
            "mois",
            "n_article",
            "designation",
            "groupe_code",
            "prix",
            "RTA",
            "TEE",
            "TVA",
            "stock_qt",
            "intial_stock_qt",
        ]
        data = [
            (
                month,
                p.n_article,
                p.designation,
                p.groupe_code,
                p.prix,
                p.rta,
                p.tee,
                p.tva,
                p.stock_qt,
                p.stock_qt_intial,
            )
            for p in products
        ]
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_showroom_transformed(self, showrooms: list[ShowRoom], month: int):
        path = self.output_folder / "showrooms_transformed.csv"
        header = ["mois", "refrence", "assigned_total_sales"]
        data = [(month, s.refrence, s.assigned_total_sales) for s in showrooms]
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_metrics(self, metrics: Metrics, month: int):
        path = self.output_folder / "calculation_metrics.csv"
        header = [
            "mois",
            "refrence",
            "assigned_total_sales",
            "calculated_total",
            "difference",
            "diffrence_ratio",
            "products_used",
        ]
        data = [
            (
                month,
                metrics.showroom.refrence,
                metrics.s_assigned,
                metrics.s_calc,
                metrics.difference,
                metrics.ratio,
                metrics.num_products_used,
            )
        ]
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_merged_products(
        self, month: int, merged_products: list[MergedProduct]
    ) -> None:
        path = self.output_folder / "merged_product.csv"
        header = [
            "mois",
            "code",
            "p1_n_article",
            "p1_designation",
            "p1_prix",
            "p2_n_article",
            "p2_designation",
            "p2_prix",
        ]
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
            )
            for ps in merged_products
        ]
        return path, header, data

    @IOTools.to_csv(mode="a")
    def write_daily_sales(self, month: int, showroom: ShowRoom) -> None:
        path = self.output_folder / "daily_sales.csv"
        header = [
            "mois",
            "showroom",
            "day",
            "c_id",
            "customer_id",
            "n_article",
            "designation",
            "groupe_code",
            "prix",
            "RTA",
            "TEE",
            "TVA",
            "Units_sold",
            "Total",
            "Total TTC",
        ]
        data = [
            (
                month,
                showroom.refrence,
                d.day,
                c.id,
                c.get_uniq_id(month, d.day, showroom.refrence),
                pur.product.n_article,
                pur.product.designation,
                pur.product.groupe_code,
                pur.product.prix,
                pur.product.rta,
                pur.product.tee,
                pur.product.tva,
                pur.units_sold,
                pur.sale_total_amount,
                pur.total_ttc,
            )
            for d in showroom.daily_sales
            for c in d.customers
            for pur in c.purchase
            if pur.units_sold
        ]
        return path, header, data

    @IOTools.to_csv(mode="w")
    def write_product_input_template_file(self, path: Path):
        header = [
            "mois",
            "n_article",
            "designation",
            "groupe_code",
            "prix",
            "RTA",
            "TEE",
            "stock_qt",
            "intial_stock_qt",
        ]
        data = []
        return path, header, data

    @IOTools.to_csv(mode="w")
    def write_showroom_input_template_file(self, path: Path):
        header = [
            "mois",
            "refrence",
            "assigned_total_sales",
        ]
        data = []
        return path, header, data
