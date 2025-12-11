import uuid
from typing import Dict

from core.payments.models import Transaction, PaymentCard
from core.exceptions.travel_errors import TravelError


class PaymentGateway:
    """Упрощённый платёжный шлюз."""

    def __init__(self, name: str):
        self.name = name
        self.transactions: Dict[str, Transaction] = {}

    def transfer(self, from_card: PaymentCard, to_card: PaymentCard, amount: float) -> Transaction:
        tx_id = str(uuid.uuid4())
        tx = Transaction(tx_id=tx_id, from_card=from_card, to_card=to_card, amount=amount)
        self.transactions[tx_id] = tx

        try:
            from_card.charge(amount)
            to_card.refund(amount)
            tx.mark_success()
        except TravelError as e:
            tx.mark_failed(str(e))
            raise

        return tx

    def get_transaction(self, tx_id: str) -> Transaction:
        return self.transactions[tx_id]
    def refund_transaction(self, tx_id: str) -> Transaction:
        original_tx = self.get_transaction(tx_id)
        if original_tx.status != "SUCCESS":
            raise TravelError("Only successful transactions can be refunded", code="REFUND_ERROR")

        refund_tx_id = str(uuid.uuid4())
        refund_tx = Transaction(
            tx_id=refund_tx_id,
            from_card=original_tx.to_card,
            to_card=original_tx.from_card,
            amount=original_tx.amount
        )
        self.transactions[refund_tx_id] = refund_tx

        try:
            original_tx.to_card.charge(original_tx.amount)
            original_tx.from_card.refund(original_tx.amount)
            refund_tx.mark_success()
        except TravelError as e:
            refund_tx.mark_failed(str(e))
            raise

        return refund_tx