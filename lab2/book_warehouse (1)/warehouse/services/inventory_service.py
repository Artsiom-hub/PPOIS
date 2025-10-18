from __future__ import annotations
from dataclasses import dataclass
from ..models.inventory import Warehouse, InventoryItem, Book
from ..exceptions import NotFoundError

@dataclass
class InventoryService:
    warehouse: Warehouse

    def reserve(self, isbn:str, qty:int) -> InventoryItem:
        item = self.warehouse.find_by_isbn(isbn)
        if not item: raise NotFoundError("isbn not found")
        item.remove(qty)
        return item

    def restock(self, isbn:str, qty:int) -> InventoryItem:
        item = self.warehouse.find_by_isbn(isbn)
        if not item: raise NotFoundError("isbn not found")
        item.add(qty)
        return item
