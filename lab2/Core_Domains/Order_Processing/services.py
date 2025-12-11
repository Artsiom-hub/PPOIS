from typing import Optional
from ..book_catalog.repository_interface import BookRepository
from .repository_interface import OrderRepository
from .models import Order
from .value_objects import OrderStatus, Money
from .exceptions import OrderNotFound, InvalidOrderOperation


class OrderService:

    def __init__(self, order_repo: OrderRepository, book_repo: BookRepository):
        self.order_repo = order_repo
        self.book_repo = book_repo

    def create_order(self, customer_id: int) -> Order:
        order = Order(
            id=self._generate_order_id(),
            customer_id=customer_id,
            items=[]
        )
        self.order_repo.save(order)
        return order

    def _generate_order_id(self):
        # Простой вариант. В реальности — UUID или счётчик в БД.
        import random
        return random.randint(100000, 999999)

    def add_book(self, order_id: int, book_id: int, qty: int):
        order = self._get_order(order_id)
        book = self.book_repo.get(book_id)

        if book.status.name == "OUT_OF_STOCK":
            raise InvalidOrderOperation("Book is out of stock")

        order.add_item(book, qty)
        self.order_repo.save(order)

    def remove_book(self, order_id: int, book_id: int):
        order = self._get_order(order_id)
        order.remove_item(book_id)
        self.order_repo.save(order)

    def pay(self, order_id: int):
        order = self._get_order(order_id)

        if order.is_empty():
            raise InvalidOrderOperation("Order is empty")

        order.set_status(OrderStatus.PAID)
        self.order_repo.save(order)

    def ship(self, order_id: int):
        order = self._get_order(order_id)

        if order.status != OrderStatus.PAID:
            raise InvalidOrderOperation("Order must be paid before shipping")

        order.set_status(OrderStatus.SHIPPED)
        self.order_repo.save(order)

    def complete(self, order_id: int):
        order = self._get_order(order_id)

        if order.status != OrderStatus.SHIPPED:
            raise InvalidOrderOperation("Order must be shipped before completion")

        order.set_status(OrderStatus.COMPLETED)
        self.order_repo.save(order)

    def cancel(self, order_id: int):
        order = self._get_order(order_id)

        if order.status == OrderStatus.COMPLETED:
            raise InvalidOrderOperation("Completed order cannot be cancelled")

        order.set_status(OrderStatus.CANCELLED)
        self.order_repo.save(order)

    # ==============================
    # Helper
    # ==============================

    def _get_order(self, order_id: int) -> Order:
        try:
            return self.order_repo.get(order_id)
        except KeyError:
            raise OrderNotFound(order_id)

    def calculate_total(self, order_id: int) -> Money:
        order = self._get_order(order_id)
        return order.total()
    def get_user_cart(self, user_id: int):
        orders = self.order_repo.list_by_customer(user_id)
        # корзина — это первый "CREATED" или "PENDING" заказ
        for o in orders:
            if o.status.name in ("CREATED", "PENDING"):
                return o
        return None

