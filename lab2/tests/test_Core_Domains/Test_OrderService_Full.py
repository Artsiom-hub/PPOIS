import pytest

from Core_Domains.Order_Processing.services import OrderService
from Core_Domains.Order_Processing.models import Order
from Core_Domains.Order_Processing.exceptions import (
    OrderNotFound, InvalidOrderOperation
)
from Core_Domains.book_catalog.models import Book
from Core_Domains.book_catalog.value_objects import Price, BookStatus
from Core_Domains.Order_Processing.value_objects import OrderStatus

# Mock repos
class BookRepo:
    def __init__(self):
        self.data = {}
    def get(self, id): return self.data[id]
    def save(self, b): self.data[b.id] = b
    def list(self): return list(self.data.values())

class OrderRepo:
    def __init__(self):
        self.data = {}
    def get(self, id):
        if id not in self.data: raise KeyError
        return self.data[id]
    def save(self, o): self.data[o.id] = o
    def delete(self, id): self.data.pop(id, None)
    def list_by_user(self, uid): return [o for o in self.data.values() if o.customer_id == uid]
    def find_open_cart(self, uid): return next((o for o in self.data.values() if o.customer_id == uid and o.status in (OrderStatus.CREATED, OrderStatus.PENDING)), None)

@pytest.fixture
def svc():
    b = BookRepo()
    o = OrderRepo()
    service = OrderService(o, b)

    # add book
    b.save(Book(id=1, title="Book", authors=[], genre=None, publisher=None,
                edition=None, price=Price(20), status=BookStatus.AVAILABLE))
    return service


def test_create_order(svc):
    order = svc.create_order(1)
    assert order.customer_id == 1

def test_add_book(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 2)
    assert o.items[0].quantity == 2

def test_add_book_out_of_stock(svc):
    b = svc.book_repo.get(1)
    b.status = BookStatus.OUT_OF_STOCK
    o = svc.create_order(1)
    with pytest.raises(InvalidOrderOperation):
        svc.add_book(o.id, 1, 1)

def test_remove_book(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.remove_book(o.id, 1)
    assert o.items == []

def test_pay(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    assert o.status == OrderStatus.PAID

def test_ship(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    svc.ship(o.id)
    assert o.status == OrderStatus.SHIPPED

def test_complete(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.pay(o.id)
    svc.ship(o.id)
    svc.complete(o.id)
    assert o.status == OrderStatus.COMPLETED

def test_cancel(svc):
    o = svc.create_order(1)
    svc.add_book(o.id, 1, 1)
    svc.cancel(o.id)
    assert o.status == OrderStatus.CANCELLED
