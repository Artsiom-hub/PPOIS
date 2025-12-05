# Infrastructure/persistence/in_memory/warehouse_repo.py

from Core_Domains.Warehouse.repository_interface import (
    CellRepository, StockRepository, StockMovementRepository, InventorySessionRepository
)


class InMemoryCellRepository(CellRepository):
    def __init__(self):
        self.data = {}

    def get(self, cell_id: int):
        return self.data[cell_id]

    def list_by_shelf(self, shelf_id: int):
        return [c for c in self.data.values() if c.shelf_id == shelf_id]

    def save(self, cell):
        self.data[cell.id] = cell
    def list(self):
        return list(self.data.values())



class InMemoryStockRepository(StockRepository):
    def __init__(self):
        self.data = {}  # ключ: (book_id, cell_id)

    def get(self, book_id: int, cell_id: int):
        return self.data[(book_id, cell_id)]

    def list_by_book(self, book_id: int):
        return [s for (b, _), s in self.data.items() if b == book_id]

    def list_by_cell(self, cell_id: int):
        return [s for (_, c), s in self.data.items() if c == cell_id]

    def save(self, stock_item):
        self.data[(stock_item.book_id, stock_item.cell_id)] = stock_item

    def delete(self, book_id: int, cell_id: int):
        del self.data[(book_id, cell_id)]
    def list_all(self):
        return list(self.data.values())



class InMemoryStockMovementRepository(StockMovementRepository):
    def __init__(self):
        self.data = {}

    def save(self, movement):
        self.data[movement.id] = movement

    def list_for_book(self, book_id: int):
        return [m for m in self.data.values() if m.book_id == book_id]


class InMemoryInventorySessionRepository(InventorySessionRepository):
    def __init__(self):
        self.data = {}

    def get(self, session_id: int):
        return self.data[session_id]

    def save(self, session):
        self.data[session.id] = session

    def list(self):
        return list(self.data.values())
