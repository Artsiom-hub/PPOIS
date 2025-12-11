import random
from Core_Domains.Payments.value_objects import TransactionStatus


class BankGateway:
    """Эмуляция внешнего банковского API."""

    def authorize_payment(self, amount: float) -> bool:
        # 95% успеха (для имитации банка)
        return random.random() > 0.05

    def get_transaction_status(self, external_id: str) -> TransactionStatus:
        # просто пример
        return TransactionStatus.SUCCESS
