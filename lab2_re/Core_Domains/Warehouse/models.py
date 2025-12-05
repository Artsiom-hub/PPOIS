from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from .value_objects import Quantity, MovementType
from .value_objects import InventoryStatus


@dataclass
class WarehouseZone:
    id: int
    name: str          # Zone A / B / C
    description: str = ""


@dataclass
class Shelf:
    id: int
    zone_id: int
    code: str          # e.g. "A-01"
    description: str = ""


@dataclass
class Cell:
    id: int
    capacity: int

    # необязательные поля
    shelf_id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    description: str = ""
    used: int = 0

    def __post_init__(self):
        # если code отсутствует — берем name
        if self.code is None and self.name is not None:
            self.code = self.name

        # если name отсутствует — берем code
        if self.name is None and self.code is not None:
            self.name = self.code




@dataclass
class StockItem:
    """
    Остаток конкретной книги в конкретной ячейке.
    """
    book_id: int
    cell_id: int
    quantity: Quantity = field(default_factory=lambda: Quantity(0))

    def increase(self, value: int):
        self.quantity = self.quantity.add(value)

    def decrease(self, value: int):
        self.quantity = self.quantity.subtract(value)


@dataclass
class StockMovement:
    id: int
    book_id: int
    from_cell_id: Optional[int]  # None если приход
    to_cell_id: Optional[int]    # None если отгрузка
    quantity: Quantity
    movement_type: MovementType
    created_at: datetime = field(default_factory=datetime.utcnow)
    comment: str = ""


@dataclass
class InventoryCheckItem:
    book_id: int
    cell_id: int
    expected: int
    actual: int

    def __post_init__(self):
        # Алиасы, которые ждут другие тесты
        self.expected_qty = self.expected
        self.actual_qty = self.actual



@dataclass
class InventoryCheckSession:
    id: int
    status: "InventoryStatus"
    started_at: datetime
    ended_at: Optional[datetime] = None

    items: List[InventoryCheckItem] = field(default_factory=list)

    def add_item_result(self, book_id: int, cell_id: int, expected: int, actual: int):
        self.items.append(
            InventoryCheckItem(
                book_id=book_id,
                cell_id=cell_id,
                expected_qty=expected,
                actual_qty=actual,
            )
        )

    def close(self):
        self.ended_at = datetime.utcnow()
