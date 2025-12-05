from dataclasses import dataclass, field
import datetime
from typing import Optional

from core.exceptions.travel_errors import (
    InsufficientFundsError,
    PaymentDeclinedError,
)
from core.users.models import Customer


@dataclass
class BankAccount:
    iban: str
    owner_name: str
    balance: float = 0.0
    currency: str = "EUR"

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Negative deposit")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientFundsError("Not enough money on bank account")
        self.balance -= amount


@dataclass
class PaymentCard:
    card_number: str
    owner: Customer
    bank_account: BankAccount
    cvv: str
    expiry_month: int
    expiry_year: int
    label: str = "Main card"

    def is_valid(self, now: Optional[datetime.date] = None) -> bool:
        now = now or datetime.date.today()
        return (self.expiry_year, self.expiry_month) >= (now.year, now.month)

    def charge(self, amount: float) -> None:
        if not self.is_valid():
            raise PaymentDeclinedError("Card expired")
        self.bank_account.withdraw(amount)

    def refund(self, amount: float) -> None:
        self.bank_account.deposit(amount)


@dataclass
class Transaction:
    tx_id: str
    from_card: PaymentCard
    to_card: PaymentCard
    amount: float
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    status: str = "PENDING"  # PENDING, SUCCESS, FAILED
    failure_reason: Optional[str] = None

    def mark_success(self) -> None:
        self.status = "SUCCESS"
        self.failure_reason = None

    def mark_failed(self, reason: str) -> None:
        self.status = "FAILED"
        self.failure_reason = reason
    def process(self) -> None:
        try:
            self.from_card.charge(self.amount)
            self.to_card.refund(self.amount)
            self.mark_success()
        except (InsufficientFundsError, PaymentDeclinedError) as e:
            self.mark_failed(str(e))