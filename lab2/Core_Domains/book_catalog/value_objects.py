from dataclasses import dataclass
from enum import Enum


class BookStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


@dataclass(frozen=True)
class Price:
    amount: float
    currency: str = "USD"

    def with_discount(self, percent: float):
        if not (0 <= percent <= 100):
            raise ValueError("Discount must be between 0 and 100%")

        new_amount = self.amount * (1 - percent / 100)
        return Price(round(new_amount, 2), self.currency)
    def multiply(self, qty: float):
        """Возвращает цену * qty как новый Price"""
        if qty < 0:
            raise ValueError("Quantity must be >= 0")
        return Price(self.amount * qty, self.currency)
