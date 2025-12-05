# Infrastructure/persistence/in_memory/payments_repo.py

from Core_Domains.Payments.repository_interface import (
    AccountRepository, TransactionRepository
)


class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self.data = {}

    def get(self, account_id: int):
        return self.data[account_id]

    def save(self, account):
        self.data[account.id] = account


class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self):
        self.data = {}

    def save(self, trx):
        self.data[trx.id] = trx

    def get(self, trx_id: int):
        return self.data[trx_id]

    def list_by_account(self, account_id: int):
        return [t for t in self.data.values()
                if t.from_account == account_id or t.to_account == account_id]
