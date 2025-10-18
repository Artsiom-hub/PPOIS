from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from ..exceptions import OrderError, ValidationError
from .inventory import Book
from .core import Address, User

@dataclass
class Customer:
    id: str
    user: User
    address: Address
    loyalty_points: int = 0

    def earn(self, pts:int): self.loyalty_points += pts
    def redeem(self, pts:int): self.loyalty_points = max(0, self.loyalty_points-pts)

@dataclass
class OrderLine:
    book: Book
    qty: int
    price: float

    def total(self) -> float: return round(self.qty * self.price, 2)
    def inc(self, n:int=1): self.qty += n

@dataclass
class Order:
    id: str
    customer: Customer
    lines: List[OrderLine] = field(default_factory=list)
    status: str = "NEW"

    def add_line(self, line:OrderLine): self.lines.append(line)
    def total(self) -> float: return round(sum(l.total() for l in self.lines), 2)
    def mark(self, st:str): self.status = st

@dataclass
class Cart:
    customer: Customer
    items: List[OrderLine] = field(default_factory=list)

    def add(self, book:Book, qty:int):
        self.items.append(OrderLine(book=book, qty=qty, price=book.price))

    def to_order(self, order_id:str) -> Order:
        if not self.items: raise OrderError("empty cart")
        return Order(id=order_id, customer=self.customer, lines=list(self.items))
