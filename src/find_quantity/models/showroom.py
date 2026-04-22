from functools import cache
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import md5
from typing import NewType

from find_quantity.models.inventory import Sale

Month = NewType("Month", int)


@dataclass
class Customer:
    id: int
    purchases: list[Sale]

    def get_uniq_id(self, month: Month, day: int, showroom_name: str) -> str:
        key = "".join((str(s) for s in [month, day, self.id, showroom_name]))
        hash_ = md5(key.encode("utf-8")).hexdigest()
        return f"C{hash_[0:15]}".upper()

    def ticket_number(self, etat_vente_number_str: str) -> str:
        return "-".join(
            [
                etat_vente_number_str,
                str(self.id),
            ]
        )


@dataclass
class DailySale:
    day: int
    sales: list[Sale]
    calendar_date: datetime
    customers: list[Customer] = field(default_factory=list)

    def __post_init__(self):
        self.calendar_date_str = self.calendar_date.strftime(r"%Y-%m-%d")

    @property
    def sale_total_amount(self) -> float:
        return sum([s.sale_total_amount for s in self.sales])

    @property
    def total_units_sold(self) -> float:
        return sum([s.units_sold for s in self.sales])

    def etat_vente_number(self, code_showroom: str) -> str:
        return cached_showroom_etat_number(self.calendar_date, code_showroom)

    def add_customer_sales(self, daily_sales: list[list[Sale]]) -> None:
        for i, sale in enumerate(daily_sales):
            pur = Customer(id=i + 1, purchases=sale)
            self.customers.append(pur)

    def __repr__(self):
        return f"DailySale {self.day} (Sold: {self.sale_total_amount} DZD | {self.total_units_sold} Units)"

    def add_sales(self, sales: list[Sale]) -> None:
        for s in sales:
            self.sales.append(s)


@dataclass
class ShowRoom:
    refrence: str
    assigned_total_sales: float
    droit_timbre: float
    code_showroom: str
    address: str
    ai: float
    rc: float

    sales: list[Sale] = field(default_factory=list)
    daily_sales: list[DailySale] = field(default_factory=list)

    def __str__(self):
        return f"Showroom {self.refrence} ({self.assigned_total_sales:,.2f} DZD)"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, value):
        if not isinstance(value, ShowRoom):
            raise TypeError(f"{type(value)} not supported")
        return self.refrence == value.refrence

    def __hash__(self):
        return hash(self.refrence)

    def add_sale(self, sale: Sale) -> None:
        self.sales.append(sale)

    def add_sales(self, sales: list[Sale]) -> None:
        for s in sales:
            self.add_sale(s)

    def add_daily_sales(
        self, day: int, month: int, year: int, sales: list[Sale]
    ) -> None:
        calendar_date = DateUtils.get_non_friday_date(month, day, year)
        self.daily_sales.append(
            DailySale(day=day, calendar_date=calendar_date, sales=sales)
        )
        # return calendar_date.day

    @property
    def calculated_total_sales(self) -> bool:
        return sum(s.sale_total_amount for s in self.sales)


class DateUtils:
    """Some Basic date utilities"""

    @classmethod
    def is_it_friday(cls, dt: datetime) -> bool:
        FRIDAY = 4
        return dt.weekday() == FRIDAY

    @classmethod
    def get_non_friday_date(cls, month: int, day: int, year: int = 2023):
        year, month, day = int(year), int(month), int(day)
        try:
            dt = datetime(year, month, day)
        except ValueError:
            # In case of an error push the sales to the first month
            dt = datetime(year, month, 1)
        if DateUtils.is_it_friday(dt):
            return DateUtils.get_non_friday_date(month, day + 1, year)
        return dt.date()


@cache
def cached_showroom_etat_number(date: datetime, code_showroom: str) -> str:
    """Cached version for faster calculation"""
    return "-".join(
        [
            date.strftime(r"%Y-%m"),
            code_showroom,
            str(date.day),
        ]
    )
