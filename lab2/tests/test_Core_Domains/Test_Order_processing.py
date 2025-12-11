# lab2re/Unit_tests/test_CoreDomains/Test_Order_Processing.py

import pytest
from datetime import date

from Core_Domains.Order_Processing.services import OrderService
from Core_Domains.Order_Processing.exceptions import (
    OrderNotFound, InvalidOrderOperation
)
from Core_Domains.Order_Processing.models import Order, OrderItem
from Core_Domains.Order_Processing.value_objects import OrderStatus, Money

from Core_Domains.book_catalog.models import Book, Author, Genre, Publisher, Edition
from Core_Domains.book_catalog.value_objects import Price, BookStatus

from Core_Domains.Order_Processing.repository_interface import OrderRepository
from Core_Domains.book_catalog.repository_interface import BookRepository


# ============================================================
#   In-memory mock repositories (fully implementing interfaces)
# ============================================================

class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.data = {}

    def get(self, order_id: int) -> Order:
        if order_id not in self.data:
            raise KeyError(order_id)
        return self.data[order_id]

    def save(self, order: Order) -> None:
        self.data[order.id] = order

    def delete(self, order_id: int) -> None:
        if order_id in self.data:
            del self.data[order_id]
        else:
            raise KeyError(order_id)

    def list_by_customer(self, customer_id: int):
        return [
            o for o in self.data.values()
            if o.customer_id == customer_id
        ]


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
        return [b for b in self.data.values()
                if title.lower() in b.title.lower()]

    def save(self, book: Book):
        self.data[book.id] = book

    def delete(self, book_id: int):
        del self.data[book_id]


# ============================================================
#                       Fixtures
# ============================================================

@pytest.fixture
def order_repo():
    return InMemoryOrderRepository()

@pytest.fixture
def book_repo():
    return InMemoryBookRepository()

@pytest.fixture
def service(order_repo, book_repo):
    return OrderService(order_repo, book_repo)

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
#                           TESTS
# ============================================================

def test_create_order(service, order_repo):
    order = service.create_order(customer_id=10)
    assert order.customer_id == 10
    assert order_repo.get(order.id).status == OrderStatus.CREATED


def test_add_book_to_order(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(20)

    service.add_book(order.id, sample_book.id, 2)

    saved = order_repo.get(order.id)
    assert len(saved.items) == 1
    assert saved.items[0].quantity == 2


def test_add_book_out_of_stock(service, book_repo, order_repo, sample_book):
    sample_book.update_status(BookStatus.OUT_OF_STOCK)
    book_repo.save(sample_book)
    order = service.create_order(20)

    with pytest.raises(InvalidOrderOperation):
        service.add_book(order.id, sample_book.id, 1)


def test_add_book_duplicate_items_combined(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)

    service.add_book(order.id, sample_book.id, 1)
    service.add_book(order.id, sample_book.id, 2)

    saved = order_repo.get(order.id)
    assert saved.items[0].quantity == 3


def test_remove_book(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(5)

    service.add_book(order.id, 1, 2)
    service.remove_book(order.id, 1)

    saved = order_repo.get(order.id)
    assert saved.items == []


def test_pay_success(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)
    service.add_book(order.id, 1, 1)

    service.pay(order.id)

    assert order_repo.get(order.id).status == OrderStatus.PAID


def test_pay_empty_order(service):
    order = service.create_order(1)

    with pytest.raises(InvalidOrderOperation):
        service.pay(order.id)


def test_ship_success(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)
    service.add_book(order.id, 1, 1)
    service.pay(order.id)

    service.ship(order.id)

    assert order_repo.get(order.id).status == OrderStatus.SHIPPED


def test_ship_fail_not_paid(service):
    order = service.create_order(1)

    with pytest.raises(InvalidOrderOperation):
        service.ship(order.id)


def test_complete_success(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)
    service.add_book(order.id, 1, 1)
    service.pay(order.id)
    service.ship(order.id)

    service.complete(order.id)

    assert order_repo.get(order.id).status == OrderStatus.COMPLETED


def test_complete_fail_wrong_state(service):
    order = service.create_order(1)

    with pytest.raises(InvalidOrderOperation):
        service.complete(order.id)


def test_cancel_success(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)
    service.add_book(order.id, 1, 1)

    service.cancel(order.id)

    assert order_repo.get(order.id).status == OrderStatus.CANCELLED


def test_cancel_fail_completed(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)
    service.add_book(order.id, 1, 1)
    service.pay(order.id)
    service.ship(order.id)
    service.complete(order.id)

    with pytest.raises(InvalidOrderOperation):
        service.cancel(order.id)


def test_order_not_found(service):
    with pytest.raises(OrderNotFound):
        service.add_book(555, 1, 1)


def test_calculate_total(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)
    order = service.create_order(1)
    service.add_book(order.id, 1, 3)

    total = service.calculate_total(order.id)

    assert total.amount == 120.0  # 40 * 3


def test_get_user_cart(service, book_repo, order_repo, sample_book):
    book_repo.save(sample_book)

    # корзина = CREATED заказ
    o1 = service.create_order(5)
    service.add_book(o1.id, sample_book.id, 1)

    cart = service.get_user_cart(5)
    assert cart is not None
    assert cart.customer_id == 5
    assert cart.status == OrderStatus.CREATED
