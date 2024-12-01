from collections import defaultdict
from pathlib import Path

from find_quantity.commons import IOTools
from find_quantity.model import Month, Product, Sale, ShowRoom


@IOTools.from_csv()
def extract_products(
    data: list[dict], path: Path) -> dict[str, list[Product]]:
    values = defaultdict(list)
    for row in data:
        p = Product(
            n_article=row["n_article"],
            designation=row["designation"],
            groupe_code=row["groupe_code"],
            prix=row["prix"],
            stock_qt=row["stock_qt"],
            tee=row['TEE'],
            rta=row['RTA']
        )
        values[row["mois"]].append(p)
    return dict(sorted(values.items()))


@IOTools.from_csv()
def extract_showrooms(
    data: list[dict], path: Path) -> dict[str, list[ShowRoom]]:
    values = defaultdict(list)
    for row in data:
        s = ShowRoom(
            refrence=row["refrence"],
            assigned_total_sales=row["assigned_total_sales"],
        )
        values[row["mois"]].append(s)
    return dict(sorted(values.items()))


@IOTools.from_csv()
def extract_calculation_report(
    data: list[dict], path: Path
) -> dict[Month, dict[str, ShowRoom]]:
    values = defaultdict(dict[str, ShowRoom])
    for row in data:
        sh = ShowRoom(
            refrence=row["Showroom"],
            assigned_total_sales=float(row["Assigned Sales"]),
        )
        values[row["mois"]][row["Showroom"]] = sh

    for row in data:
        s = Sale(
            product=Product(
                n_article=row["N-Article"],
                designation=row["Designation"],
                groupe_code=row["Groupe-Code"],
                prix=float(row["Prix"]),
                stock_qt=int(row["Current_Stock"]),
                tee=float(row['TEE']),
                rta=float(row['RTA']),
            ),
            units_sold=int(row["Quantite"]),
        )
        s.product.stock_qt_intial = int(row["Initial_stock"])
        values[row["mois"]].get(row["Showroom"]).add_sale(s)
    return values


@IOTools.from_csv()
def load_merged_products(data: list[dict], path: Path):
    values: dict = defaultdict(dict)
    for row in data:
        values[(row['mois'], row["code"])] = row
    return values


@IOTools.from_csv()
def load_raw_file(data: list[dict], path: Path):
    return data


if __name__ == "__main__":
    produit = extract_products()
    showrooms = extract_showrooms()
    print(showrooms)
