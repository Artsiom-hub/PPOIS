# lab2re/Unit_tests/test_CoreDomains/Test_book_catalog.py

import pytest

from Core_Domains.book_catalog.services import BookCatalogService
from Core_Domains.book_catalog.exceptions import BookNotFound, InvalidSearchFilter
from Core_Domains.book_catalog.models import (
    Book, Author, Genre, Publisher, Edition
)
from Core_Domains.book_catalog.value_objects import Price, BookStatus
from Core_Domains.book_catalog.repository_interface import BookRepository

from datetime import date


# ============================================================
#     In-memory mock repository implementing BookRepository
# ============================================================

class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self.data = {}

    def get(self, book_id: int) -> Book:
        if book_id not in self.data:
            raise KeyError(book_id)
        return self.data[book_id]

    def list(self):
        return list(self.data.values())

    def find_by_title(self, title: str):
        return [
            b for b in self.data.values()
            if title.lower() in b.title.lower()
        ]

    def save(self, book: Book):
        self.data[book.id] = book

    def delete(self, book_id: int):
        if book_id not in self.data:
            raise KeyError(book_id)
        del self.data[book_id]


# ============================================================
#                       Test Fixtures
# ============================================================

@pytest.fixture
def repo():
    return InMemoryBookRepository()


@pytest.fixture
def service(repo):
    return BookCatalogService(repo)


@pytest.fixture
def sample_book():
    return Book(
        id=1,
        title="Clean Code",
        authors=[Author(1, "Robert C. Martin")],
        genre=Genre(1, "Programming"),
        publisher=Publisher(1, "Prentice Hall"),
        edition=Edition("9780132350884", date(2008, 8, 1), 464),
        price=Price(40.0),
        status=BookStatus.AVAILABLE
    )


# ============================================================
#                       TESTS
# ============================================================

def test_add_book(service, repo, sample_book):
    service.add_book(sample_book)
    assert repo.get(1).title == "Clean Code"


def test_get_book_success(service, repo, sample_book):
    repo.save(sample_book)
    b = service.get_book(1)
    assert b.title == "Clean Code"


def test_get_book_not_found(service):
    with pytest.raises(BookNotFound):
        service.get_book(999)


def test_list_all_books(service, repo, sample_book):
    repo.save(sample_book)
    assert len(service.list_all()) == 1


def test_search_by_title(service, repo, sample_book):
    repo.save(sample_book)
    results = service.search(title="clean")
    assert len(results) == 1
    assert results[0].id == 1


def test_search_by_title_no_match(service, repo, sample_book):
    repo.save(sample_book)
    results = service.search(title="Python")
    assert results == []


def test_search_by_author(service, repo, sample_book):
    repo.save(sample_book)
    results = service.search(author="martin")
    assert len(results) == 1


def test_search_by_genre(service, repo, sample_book):
    repo.save(sample_book)
    results = service.search(genre="programming")
    assert len(results) == 1


def test_search_by_status(service, repo, sample_book):
    sample_book.update_status(BookStatus.RESERVED)
    repo.save(sample_book)

    results = service.search(status=BookStatus.RESERVED)
    assert len(results) == 1


def test_update_price(service, repo, sample_book):
    repo.save(sample_book)
    service.update_price(1, Price(99.0))
    assert repo.get(1).price.amount == 99.0


def test_reserve_available_book(service, repo, sample_book):
    repo.save(sample_book)
    service.reserve_book(1)
    assert repo.get(1).status == BookStatus.RESERVED


def test_reserve_unavailable_book(service, repo, sample_book):
    sample_book.update_status(BookStatus.DISCONTINUED)
    repo.save(sample_book)

    with pytest.raises(InvalidSearchFilter):
        service.reserve_book(1)


def test_release_reservation(service, repo, sample_book):
    sample_book.update_status(BookStatus.RESERVED)
    repo.save(sample_book)

    service.release_reservation(1)
    assert repo.get(1).status == BookStatus.AVAILABLE


def test_release_reservation_not_reserved(service, repo, sample_book):
    repo.save(sample_book)

    with pytest.raises(InvalidSearchFilter):
        service.release_reservation(1)


def test_discontinue_book(service, repo, sample_book):
    repo.save(sample_book)
    service.discontinue_book(1)
    assert repo.get(1).status == BookStatus.DISCONTINUED


def test_remove_book(service, repo, sample_book):
    repo.save(sample_book)
    service.remove_book(1)

    with pytest.raises(KeyError):
        repo.get(1)


def test_remove_nonexistent_book(service):
    with pytest.raises(BookNotFound):
        service.remove_book(42)
