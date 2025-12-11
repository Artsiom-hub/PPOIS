import pytest
from unittest.mock import MagicMock

from Core_Domains.Order_Processing.services import OrderService  # :contentReference[oaicite:0]{index=0}
from Core_Domains.Order_Processing.exceptions import (
    OrderNotFound,
    InvalidOrderOperation
)
from Core_Domains.Order_Processing.value_objects import OrderStatus, Money
from Core_Domains.book_catalog.models import Book
from Core_Domains.book_catalog.value_objects import Price, BookStatus
from Core_Domains.Order_Processing.models import Order, OrderItem


# ===============================================================
#               MOCK REPOSITORIES
# ===============================================================

class OrderRepoMock:
    def __init__(self):
        self.data = {}

    def save(self, order):
        self.data[order.id] = order

    def get(self, order_id):
        if order_id not in self.data:
            raise KeyError
        return self.data[order_id]

    def list_by_customer(self, user_id):
        return [o for o in self.data.values() if o.customer_id == user_id]


class BookRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, book_id):
        if book_id not in self.data:
            raise KeyError
        return self.data[book_id]

    def save(self, b):
        self.data[b.id] = b


# ===============================================================
#                FIXTURE
# ===============================================================

@pytest.fixture
def svc():
    o = OrderRepoMock()
    b = BookRepoMock()

    # add book
    b.data[1] = Book(
        id=1,
        title="Test",
        authors=[],
        genre=None,
        publisher=None,
        edition=None,
        price=Price(10),
        status=BookStatus.AVAILABLE
    )

    return OrderService(o, b)


# ===============================================================
#             TESTS FOR ALL BRANCHES OF OrderService
# ===============================================================

def test_get_order_not_found(svc):
    with pytest.raises(OrderNotFound):
        svc._get_order(999)


def test_create_order(svc):
    o = svc.create_order(1)
    assert o.customer_id == 1
    assert o.items == []


def test_add_book_ok(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 2)
    assert o.items[0].quantity == 2


def test_add_book_out_of_stock(svc):
    svc.book_repo.data[1].status = BookStatus.OUT_OF_STOCK
    o = svc.create_order(1)
    with pytest.raises(InvalidOrderOperation):
        svc.add_book(o.id, 1, 1)


def test_remove_book(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 3)
    svc.remove_book(o.id, 1)
    assert o.items == []


def test_pay_order_empty(svc):
    o = svc.create_order(1)
    with pytest.raises(InvalidOrderOperation):
        svc.pay(o.id)


def test_pay_ok(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    assert o.status == OrderStatus.PAID


def test_ship_not_paid(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    with pytest.raises(InvalidOrderOperation):
        svc.ship(o.id)


def test_ship_ok(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    svc.ship(o.id)
    assert o.status == OrderStatus.SHIPPED


def test_complete_not_shipped(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    with pytest.raises(InvalidOrderOperation):
        svc.complete(o.id)


def test_complete_ok(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    svc.ship(o.id)
    svc.complete(o.id)
    assert o.status == OrderStatus.COMPLETED


def test_cancel_completed(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    svc.ship(o.id)
    svc.complete(o.id)

    with pytest.raises(InvalidOrderOperation):
        svc.cancel(o.id)


def test_cancel_ok(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.cancel(o.id)
    assert o.status == OrderStatus.CANCELLED


def test_calculate_total(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 2)
    total = svc.calculate_total(o.id)
    assert total.amount == 20


def test_get_user_cart_first_created(svc):
    o1 = svc.create_order(5)
    o2 = svc.create_order(5)
    o1.status = OrderStatus.COMPLETED
    o2.status = OrderStatus.PENDING

    assert svc.get_user_cart(5).id == o2.id


def test_get_user_cart_none(svc):
    o1 = svc.create_order(10)
    o1.status = OrderStatus.COMPLETED
    assert svc.get_user_cart(10) is None
