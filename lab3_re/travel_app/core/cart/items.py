from dataclasses import dataclass
from typing import Any


@dataclass
class CartItem:
    item_type: str      # e.g., "FLIGHT", "HOTEL", etc.
    reference: Any      # ссылка на объект бронирования или товар
    price: float
    quantity: int = 1

    def line_total(self) -> float:
        return self.price * self.quantity

    def increase_qty(self, delta: int = 1) -> None:
        self.quantity += delta
