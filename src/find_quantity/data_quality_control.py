from collections import defaultdict
from dataclasses import dataclass

from find_quantity.model import Product, Month
from find_quantity.transformer_csv import ProductTransformer


@dataclass
class ValidateProductQuantity:
    month: int
    product_name: str
    calc_stock_qt: int
    calc_stock_qt_initial: int
    calc_all_units_sold: int
    # calc_stock_qt_initial_min: int
    raw_data_stock_initial: int = 0

    @property
    def calc_stock_diff(self) -> int:
        return self.calc_stock_qt_initial - (self.calc_stock_qt + self.calc_all_units_sold)

    @property
    def is_calc_correct(self) -> bool:
        return self.calc_stock_diff == 0

    @property
    def was_raw_data_read_correctly(self) -> bool:
        return self.raw_data_stock_initial == self.calc_stock_qt_initial


@dataclass
class ProductRawDataSimplified:
    month: int
    product_name: str
    stock_qt_initial: int


def validate_calculated_products(calculation_report: dict) -> list[ValidateProductQuantity]:
    all_sales_monthly = defaultdict(lambda: defaultdict(list))
    for month, showrooms in calculation_report.items():
        for sh in showrooms.values(): 
            for sale in sh.sales:
                product_name = sale.product.n_article
                all_sales_monthly[month][product_name].append(sale)

    product_validation: list[ValidateProductQuantity] = list()
    for month, sales in all_sales_monthly.items():
        for product_name, sales in sales.items():
            stock_qt=min([int(s.product.stock_qt) for s in sales])
            stock_qt_intial=max([int(s.product.stock_qt_intial) for s in sales])
            all_units_sold = sum([int(s.units_sold) for s in sales])
            v = ValidateProductQuantity(
                month=month,
                product_name=product_name,
                calc_stock_qt=stock_qt,
                calc_stock_qt_initial=stock_qt_intial,
                calc_all_units_sold=all_units_sold
            )
            product_validation.append(v)
    return product_validation


def validate_extracted_product_raw_data(raw_products: dict[Month, list[Product]]) -> list[ProductRawDataSimplified]:
    cleaned_products: dict[Month, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for month, products in raw_products.items():
        products = ProductTransformer(products=products).load()
        for p in products:
            cleaned_products[month][p.n_article].append(p)
    
    parsed_products: list[ProductRawDataSimplified] = list()
    for month, name_products in cleaned_products.items():
        for product_name, products in name_products.items():
            stock_qt_intial = sum([p.stock_qt for p in products])
            v = ProductRawDataSimplified(
                month=month,
                product_name=product_name,
                stock_qt_initial=stock_qt_intial
            )
            parsed_products.append(v)
    return parsed_products


def product_validation(validation_data_product_calc: list[ValidateProductQuantity],
                       simplied_product_raw_data: list[ProductRawDataSimplified]
                    ) -> list[ValidateProductQuantity]:
    for v in validation_data_product_calc:
        for p in simplied_product_raw_data:
            if v.product_name == p.product_name and v.month == p.month:
                v.raw_data_stock_initial = p.stock_qt_initial
                break
    return validation_data_product_calc
    
def main():
    # RAW_PRODUCTS_DATA: Path = Path(r'data\produits.csv')
    # raw_products = extract_products(RAW_PRODUCTS_DATA)
    # product_validation
    pass
    
    



if __name__ == '__main__':
    main()
