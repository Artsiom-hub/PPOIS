from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from ..exceptions import OutOfStockError, NegativeQuantityError, ValidationError, NotFoundError

@dataclass
class Author:
    id: str
    name: str
    bio: str = ""
    rating: float = 0.0

    def add_bio(self, text:str): self.bio += (" " + text).strip()
    def upvote(self, delta:float=0.1): self.rating += delta

@dataclass
class Publisher:
    id: str
    name: str
    address: str = ""

    def label(self) -> str: return f"{self.name} ({self.address})"
    def relocate(self, new_addr:str): self.address = new_addr

@dataclass
class Category:
    id: str
    name: str
    parent_id: Optional[str] = None

    def is_root(self) -> bool: return self.parent_id is None
    def path(self) -> str: return self.name if self.is_root() else f"{self.parent_id}>{self.name}"

@dataclass
class Book:
    isbn: str
    title: str
    author: Author
    publisher: Publisher
    price: float
    category: Category
    tags: List[str] = field(default_factory=list)

    def add_tag(self, tag:str): 
        if tag not in self.tags: self.tags.append(tag)

    def price_with_tax(self, rate:float) -> float:
        return round(self.price * (1+rate), 2)

@dataclass
class Shelf:
    id: str
    name: str
    capacity: int
    level: int = 0

    def can_place(self, qty:int) -> bool: return qty <= self.capacity
    def rename(self, name:str): self.name = name

@dataclass
class Bin:
    id: str
    shelf: Shelf
    label: str
    max_weight: float = 50.0

    def move_to(self, shelf:Shelf): self.shelf = shelf
    def relabel(self, new_label:str): self.label = new_label

@dataclass
class InventoryItem:
    book: Book
    quantity: int
    bin: Bin

    def add(self, qty:int):
        if qty < 0: raise NegativeQuantityError("qty < 0")
        self.quantity += qty

    def remove(self, qty:int):
        if qty < 0: raise NegativeQuantityError("qty < 0")
        if self.quantity < qty: raise OutOfStockError("not enough stock")
        self.quantity -= qty

@dataclass
class Warehouse:
    id: str
    name: str
    bins: Dict[str, InventoryItem] = field(default_factory=dict)

    def put(self, item:InventoryItem):
        self.bins[item.bin.id] = item

    def get(self, bin_id:str) -> InventoryItem:
        if bin_id not in self.bins: raise NotFoundError("bin not found")
        return self.bins[bin_id]

    def total_items(self) -> int:
        return sum(i.quantity for i in self.bins.values())

    def find_by_isbn(self, isbn:str) -> Optional[InventoryItem]:
        for item in self.bins.values():
            if item.book.isbn == isbn:
                return item
        return None
