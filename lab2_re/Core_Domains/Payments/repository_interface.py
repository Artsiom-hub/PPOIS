from abc import ABC, abstractmethod
from typing import List
from .models import Account, Transaction


class AccountRepository(ABC):

    @abstractmethod
    def get(self, account_id: int) -> Account:
        pass

    @abstractmethod
    def save(self, account: Account) -> None:
        pass


class TransactionRepository(ABC):

    @abstractmethod
    def save(self, trx: Transaction) -> None:
        pass

    @abstractmethod
    def get(self, trx_id: int) -> Transaction:
        pass

    @abstractmethod
    def list_by_account(self, account_id: int) -> List[Transaction]:
        pass
