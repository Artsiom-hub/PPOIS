from enum import Enum
from dataclasses import dataclass


class MovementType(Enum):
    INBOUND = "inbound"        # прихod на склад
    OUTBOUND = "outbound"      # отгрузка
    RELOCATION = "relocation"  # перемещение между ячейками
    ADJUSTMENT = "adjustment"  # корректировка (инвентаризация)
    MOVE = "move"             # перемещение между ячейками
class InventoryStatus(Enum):
    STARTED = "started"
    FINISHED = "finished"


@dataclass(frozen=True)
class Quantity:
    amount: int

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Quantity cannot be negative")

    def add(self, value: int) -> "Quantity":
        return Quantity(self.amount + value)

    def subtract(self, value: int) -> "Quantity":
        if value > self.amount:
            raise ValueError("Not enough stock")
        return Quantity(self.amount - value)
