from __future__ import annotations
from dataclasses import dataclass
from ..models.finance import PaymentGateway, Account, Transaction
from ..exceptions import PaymentError

@dataclass
class PaymentService:
    gateway: PaymentGateway

    def transfer(self, src:Account, dst:Account, amount:float) -> Transaction:
        return self.gateway.transfer(src, dst, amount)

    def refund(self, tx:Transaction) -> Transaction:
        return self.gateway.refund(tx)
