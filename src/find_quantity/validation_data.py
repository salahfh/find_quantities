from dataclasses import dataclass


@dataclass
class ValidationShowroomData:
    mois: int
    showroom: str
    difference_in_sales: float
