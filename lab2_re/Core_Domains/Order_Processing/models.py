from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from .value_objects import Money, OrderStatus
from ..book_catalog.models import Book


@dataclass
class OrderItem:
    book: Book
    quantity: int

    def total_price(self) -> Money:
        return self.book.price.multiply(self.quantity)


@dataclass
class Order:
    id: int
    customer_id: int
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_item(self, book: Book, qty: int):
        if qty <= 0:
            raise ValueError("Quantity must be positive")

        for item in self.items:
            if item.book.id == book.id:
                item.quantity += qty
                self.touch()
                return

        self.items.append(OrderItem(book=book, quantity=qty))
        self.touch()
    def update_status(self, new_status: OrderStatus):
        self.set_status(new_status)

    def remove_item(self, book_id: int):
        self.items = [i for i in self.items if i.book.id != book_id]
        self.touch()

    def total(self) -> Money:
        total_amount = 0
        currency = "USD"

        for item in self.items:
            total_amount += item.total_price().amount
            currency = item.total_price().currency

        return Money(total_amount, currency)

    def set_status(self, new_status: OrderStatus):
        self.status = new_status
        self.touch()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def touch(self):
        self.updated_at = datetime.utcnow()
