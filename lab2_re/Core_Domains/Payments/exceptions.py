class PaymentError(Exception):
    pass


class AccountNotFound(PaymentError):
    def __init__(self, acc_id: int):
        super().__init__(f"Account {acc_id} not found")


class InsufficientFunds(PaymentError):
    def __init__(self):
        super().__init__("Insufficient funds")


class TransactionNotFound(PaymentError):
    def __init__(self, trx_id: int):
        super().__init__(f"Transaction {trx_id} not found")
