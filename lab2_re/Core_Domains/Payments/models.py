from dataclasses import dataclass, field
from datetime import datetime
from .value_objects import Money, TransactionType, TransactionStatus


@dataclass
class Account:
    id: int
    owner_id: int
    balance: Money

    def deposit(self, amount: Money):
        self.balance = self.balance.add(amount)

    def withdraw(self, amount: Money):
        self.balance = self.balance.subtract(amount)


@dataclass
class Transaction:
    id: int
    from_account: int
    to_account: int
    amount: Money
    type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_success(self):
        self.status = TransactionStatus.SUCCESS

    def mark_failed(self):
        self.status = TransactionStatus.FAILED
