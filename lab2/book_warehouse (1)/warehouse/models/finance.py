from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from ..exceptions import InsufficientFundsError, CurrencyMismatchError, PaymentError, ValidationError

@dataclass
class Currency:
    code: str
    symbol: str
    rate_to_usd: float = 1.0

    def convert_to(self, amount:float, target:'Currency') -> float:
        usd = amount * self.rate_to_usd
        return usd / (target.rate_to_usd or 1.0)

@dataclass
class Account:
    id: str
    owner: str
    currency: Currency
    balance: float = 0.0

    def deposit(self, amount:float): self.balance += amount
    def withdraw(self, amount:float):
        if self.balance < amount: raise InsufficientFundsError("balance < amount")
        self.balance -= amount

@dataclass
class Card:
    number: str
    account: Account
    cvv_hash: str
    expires: str

    def validate_cvv(self, hasher:'PasswordHasher', candidate:str, salt:str) -> bool:
        return hasher.verify(candidate, salt, self.cvv_hash)

@dataclass
class Transaction:
    id: str
    source: Account
    target: Account
    amount: float
    currency: Currency
    status: str = "NEW"

    def mark(self, st:str): self.status = st
    def is_success(self) -> bool: return self.status == "OK"

@dataclass
class PaymentGateway:
    name: str
    fee_rate: float = 0.01
    transactions: List[Transaction] = field(default_factory=list)

    def transfer(self, src:Account, dst:Account, amount:float) -> Transaction:
        if src.currency.code != dst.currency.code:
            raise CurrencyMismatchError("currency mismatch")
        fee = amount * self.fee_rate
        if src.balance < amount + fee: raise InsufficientFundsError("not enough for fee")
        src.withdraw(amount + fee)
        dst.deposit(amount)
        tx = Transaction(id=f"tx-{len(self.transactions)+1}", source=src, target=dst, amount=amount, currency=src.currency, status="OK")
        self.transactions.append(tx)
        return tx

    def refund(self, tx:Transaction) -> Transaction:
        if not tx.is_success(): raise PaymentError("only successful tx can be refunded")
        tx.target.withdraw(tx.amount)
        tx.source.deposit(tx.amount)
        tx.mark("REFUNDED")
        return tx
