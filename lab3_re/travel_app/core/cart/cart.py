from dataclasses import dataclass, field
from typing import List

from core.users.models import Customer
from .items import CartItem


@dataclass
class Cart:
    customer: Customer
    items: List[CartItem] = field(default_factory=list)

    def add_item(self, item: CartItem) -> None:
        self.items.append(item)

    def total(self) -> float:
        return sum(i.line_total() for i in self.items)

    def clear(self) -> None:
        self.items.clear()
