from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class TariffOption:
    months: int
    base_price: int
    discount_price: int
    discount_percent: int