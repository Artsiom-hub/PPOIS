from abc import ABC, abstractmethod
from .value_objects import Money


class PaymentGateway(ABC):

    @abstractmethod
    def authorize(self, amount: Money) -> bool:
        """Проверка можно ли снять сумму с карты"""
        pass

    @abstractmethod
    def capture(self, amount: Money) -> bool:
        """Фактическое списание"""
        pass

    @abstractmethod
    def refund(self, amount: Money) -> bool:
        """Возврат средств"""
        pass
