# Infrastructure/persistence/in_memory/order_repo.py

from Core_Domains.Order_Processing.repository_interface import OrderRepository
from Core_Domains.Order_Processing.models import Order


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self.data = {}

    def get(self, order_id: int) -> Order:
        return self.data[order_id]

    def save(self, order: Order):
        self.data[order.id] = order

    def delete(self, order_id: int):
        del self.data[order_id]

    def list_by_customer(self, customer_id: int):
        return [o for o in self.data.values() if o.customer_id == customer_id]
    def list_all(self):
        return list(self.data.values())

    def list_by_user(self, user_id: int):
        return [o for o in self.data.values() if o.customer_id == user_id]

    def find_open_cart(self, user_id: int):
        for o in self.data.values():
            if o.customer_id == user_id and o.status.name in ("CREATED", "PENDING"):
                return o
        return None
