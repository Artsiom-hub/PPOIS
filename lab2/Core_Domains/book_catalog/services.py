from typing import List, Optional
from .models import Book
from .value_objects import Price, BookStatus
from .exceptions import BookNotFound, InvalidSearchFilter
from .repository_interface import BookRepository


class BookCatalogService:

    def __init__(self, repo: BookRepository):
        self.repo = repo

    def search(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        status: Optional[BookStatus] = None
    ) -> List[Book]:
        books = self.repo.list()

        if title:
            books = [b for b in books if title.lower() in b.title.lower()]

        if author:
            books = [
                b for b in books
                if any(author.lower() in a.name.lower() for a in b.authors)
            ]

        if genre:
            books = [b for b in books if b.genre.name.lower() == genre.lower()]

        if status:
            books = [b for b in books if b.status == status]

        return books

    def get_book(self, book_id: int) -> Book:
        try:
            return self.repo.get(book_id)
        except KeyError:
            raise BookNotFound(book_id)

    def update_price(self, book_id: int, new_price: Price):
        book = self.get_book(book_id)
        book.update_price(new_price)
        self.repo.save(book)

    def reserve_book(self, book_id: int):
        book = self.get_book(book_id)

        if book.status != BookStatus.AVAILABLE:
            raise InvalidSearchFilter("Book cannot be reserved")

        book.update_status(BookStatus.RESERVED)
        self.repo.save(book)

    def release_reservation(self, book_id: int):
        book = self.get_book(book_id)

        if book.status != BookStatus.RESERVED:
            raise InvalidSearchFilter("Book is not reserved")

        book.update_status(BookStatus.AVAILABLE)
        self.repo.save(book)

    def discontinue_book(self, book_id: int):
        book = self.get_book(book_id)
        book.update_status(BookStatus.DISCONTINUED)
        self.repo.save(book)
    def add_book(self, book: Book):
        """Создание новой книги в каталоге."""
        self.repo.save(book)
        return book
    def remove_book(self, book_id: int):
        """Удаление книги из каталога по её ID."""
        try:
            self.repo.delete(book_id)
        except KeyError:
            raise BookNotFound(book_id)
    def list_all(self):
        return self.repo.list()

