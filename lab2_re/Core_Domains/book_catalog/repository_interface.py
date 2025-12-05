from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Book


class BookRepository(ABC):

    @abstractmethod
    def get(self, book_id: int) -> Book:
        pass

    @abstractmethod
    def list(self) -> List[Book]:
        pass

    @abstractmethod
    def find_by_title(self, title: str) -> List[Book]:
        pass

    @abstractmethod
    def save(self, book: Book) -> None:
        pass

    @abstractmethod
    def delete(self, book_id: int) -> None:
        pass
