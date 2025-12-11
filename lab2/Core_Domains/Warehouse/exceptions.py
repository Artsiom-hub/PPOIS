class WarehouseError(Exception):
    pass


class CellNotFound(WarehouseError):
    def __init__(self, cell_id: int):
        super().__init__(f"Cell {cell_id} not found")


class StockItemNotFound(WarehouseError):
    def __init__(self, book_id: int, cell_id: int):
        super().__init__(f"Stock item not found for book {book_id} in cell {cell_id}")


class NotEnoughStock(WarehouseError):
    def __init__(self):
        super().__init__("Not enough stock in cell")


class InventorySessionNotFound(WarehouseError):
    def __init__(self, session_id: int):
        super().__init__(f"Inventory session {session_id} not found")
class DuplicateInventorySessionError(WarehouseError):
    def __init__(self, session_id: int):
        super().__init__(f"Inventory session {session_id} already exists")
