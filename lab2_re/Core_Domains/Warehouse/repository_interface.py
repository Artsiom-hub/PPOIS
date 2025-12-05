from abc import ABC, abstractmethod
from typing import List, Optional
from .models import WarehouseZone, Shelf, Cell, StockItem, StockMovement, InventoryCheckSession


class ZoneRepository(ABC):

    @abstractmethod
    def get(self, zone_id: int) -> WarehouseZone:
        pass

    @abstractmethod
    def list(self) -> List[WarehouseZone]:
        pass

    @abstractmethod
    def save(self, zone: WarehouseZone) -> None:
        pass


class ShelfRepository(ABC):

    @abstractmethod
    def get(self, shelf_id: int) -> Shelf:
        pass

    @abstractmethod
    def list_by_zone(self, zone_id: int) -> List[Shelf]:
        pass

    @abstractmethod
    def save(self, shelf: Shelf) -> None:
        pass


class CellRepository(ABC):

    @abstractmethod
    def get(self, cell_id: int) -> Cell:
        pass

    @abstractmethod
    def list_by_shelf(self, shelf_id: int) -> List[Cell]:
        pass

    @abstractmethod
    def save(self, cell: Cell) -> None:
        pass


class StockRepository(ABC):

    @abstractmethod
    def get(self, book_id: int, cell_id: int) -> StockItem:
        pass

    @abstractmethod
    def list_by_book(self, book_id: int) -> List[StockItem]:
        pass

    @abstractmethod
    def list_by_cell(self, cell_id: int) -> List[StockItem]:
        pass

    @abstractmethod
    def save(self, stock_item: StockItem) -> None:
        pass

    @abstractmethod
    def delete(self, book_id: int, cell_id: int) -> None:
        pass


class StockMovementRepository(ABC):

    @abstractmethod
    def save(self, movement: StockMovement) -> None:
        pass

    @abstractmethod
    def list_for_book(self, book_id: int) -> List[StockMovement]:
        pass


class InventorySessionRepository(ABC):

    @abstractmethod
    def get(self, session_id: int) -> InventoryCheckSession:
        pass

    @abstractmethod
    def save(self, session: InventoryCheckSession) -> None:
        pass

    @abstractmethod
    def list(self) -> List[InventoryCheckSession]:
        pass
