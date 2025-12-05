from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    PENDING = "pending"     
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Different currencies")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, qty: int) -> "Money":
        return Money(self.amount * qty, self.currency)
