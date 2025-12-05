from typing import List
from abc import ABC, abstractmethod
from .models import Order


class OrderRepository(ABC):

    @abstractmethod
    def get(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass

    @abstractmethod
    def delete(self, order_id: int) -> None:
        pass

    @abstractmethod
    def list_by_customer(self, customer_id: int) -> List[Order]:
        pass
