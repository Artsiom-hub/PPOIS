# Infrastructure/persistence/in_memory/book_repo.py

from Core_Domains.book_catalog.repository_interface import BookRepository
from Core_Domains.book_catalog.models import Book


class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self.data = {}  # ключ = id

    def get(self, book_id: int) -> Book:
        return self.data[book_id]

    def list(self):
        return list(self.data.values())

    def find_by_title(self, title: str):
        title = title.lower()
        return [b for b in self.data.values() if title in b.title.lower()]

    def save(self, book: Book):
        self.data[book.id] = book

    def delete(self, book_id: int):
        del self.data[book_id]
