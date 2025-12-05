from dataclasses import dataclass
from enum import Enum


class TransactionType(Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"


class TransactionStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Different currencies")
        if other.amount > self.amount:
            raise ValueError("Insufficient funds")
        return Money(self.amount - other.amount, self.currency)

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Different currencies")
        return Money(self.amount + other.amount, self.currency)
