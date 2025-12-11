from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from .value_objects import Price, BookStatus


@dataclass
class Author:
    id: int
    name: str
    bio: Optional[str] = None


@dataclass
class Genre:
    id: int
    name: str


@dataclass
class Publisher:
    id: int
    name: str
    address: Optional[str] = None


@dataclass
class Edition:
    isbn: str
    publish_date: date
    pages: int


@dataclass
class Book:
    id: int
    title: str
    authors: List[Author]
    genre: Genre
    publisher: Publisher
    edition: Edition
    price: Price
    status: BookStatus = BookStatus.AVAILABLE
    description: Optional[str] = None

    def update_price(self, new_price: Price):
        self.price = new_price

    def update_status(self, new_status: BookStatus):
        self.status = new_status

    def add_author(self, author: Author):
        if author not in self.authors:
            self.authors.append(author)

    def remove_author(self, author: Author):
        if author in self.authors:
            self.authors.remove(author)
