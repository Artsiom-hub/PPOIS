# lab2re/Unit_tests/test_CoreDomains/Test_Payments.py

import pytest

from Core_Domains.Payments.services import PaymentService
from Core_Domains.Payments.exceptions import (
    AccountNotFound, InsufficientFunds, TransactionNotFound, PaymentError
)
from Core_Domains.Payments.models import Account, Transaction
from Core_Domains.Payments.value_objects import Money, TransactionStatus, TransactionType
from Core_Domains.Payments.repository_interface import (
    AccountRepository, TransactionRepository
)
from Core_Domains.Payments.gateway_interface import PaymentGateway


# ============================================================
#   Mock Repositories
# ============================================================

class InMemoryAccountRepo(AccountRepository):
    def __init__(self):
        self.data = {}

    def get(self, account_id: int) -> Account:
        if account_id not in self.data:
            raise KeyError(account_id)
        return self.data[account_id]

    def save(self, account: Account) -> None:
        self.data[account.id] = account


class InMemoryTransactionRepo(TransactionRepository):
    def __init__(self):
        self.data = {}

    def save(self, trx: Transaction) -> None:
        self.data[trx.id] = trx

    def get(self, trx_id: int) -> Transaction:
        if trx_id not in self.data:
            raise KeyError(trx_id)
        return self.data[trx_id]

    def list_by_account(self, account_id: int):
        return [
            t for t in self.data.values()
            if t.from_account == account_id or t.to_account == account_id
        ]


# ============================================================
#   Mock Gateway
# ============================================================

class FakeGateway(PaymentGateway):
    def __init__(self, authorize_ok=True, capture_ok=True, refund_ok=True):
        self.authorize_ok = authorize_ok
        self.capture_ok = capture_ok
        self.refund_ok = refund_ok

    def authorize(self, amount: Money) -> bool:
        return self.authorize_ok

    def capture(self, amount: Money) -> bool:
        return self.capture_ok

    def refund(self, amount: Money) -> bool:
        return self.refund_ok


# ============================================================
#                    Fixtures
# ============================================================

@pytest.fixture
def acc_repo():
    return InMemoryAccountRepo()

@pytest.fixture
def trx_repo():
    return InMemoryTransactionRepo()

@pytest.fixture
def gateway():
    return FakeGateway()

@pytest.fixture
def service(acc_repo, trx_repo, gateway):
    return PaymentService(acc_repo, trx_repo, gateway)


# ============================================================
#                       TESTS
# ============================================================


# ---------- TRANSFER TESTS ----------

def test_transfer_success(service, acc_repo, trx_repo):
    acc_repo.save(Account(id=1, owner_id=1, balance=Money(100)))
    acc_repo.save(Account(id=2, owner_id=2, balance=Money(50)))

    trx = service.transfer(1, 2, Money(30))

    assert trx.status == TransactionStatus.SUCCESS
    assert acc_repo.get(1).balance.amount == 70
    assert acc_repo.get(2).balance.amount == 80
    assert trx.id in trx_repo.data


def test_transfer_insufficient_funds(service, acc_repo, trx_repo):
    acc_repo.save(Account(id=1, owner_id=1, balance=Money(10)))
    acc_repo.save(Account(id=2, owner_id=2, balance=Money(50)))

    with pytest.raises(InsufficientFunds):
        service.transfer(1, 2, Money(30))


def test_transfer_account_not_found(service):
    with pytest.raises(AccountNotFound):
        service.transfer(999, 2, Money(10))


# ---------- PAY ORDER TESTS ----------

def test_pay_order_success(acc_repo, trx_repo):
    # Gateway OK
    gateway = FakeGateway(authorize_ok=True, capture_ok=True)
    service = PaymentService(acc_repo, trx_repo, gateway)

    acc_repo.save(Account(id=1, owner_id=2, balance=Money(100)))

    trx = service.pay_order(1, Money(40))
    assert trx.status == TransactionStatus.SUCCESS
    assert acc_repo.get(1).balance.amount == 60


def test_pay_order_authorize_fail(acc_repo, trx_repo):
    gateway = FakeGateway(authorize_ok=False)
    service = PaymentService(acc_repo, trx_repo, gateway)

    acc_repo.save(Account(id=1, owner_id=2, balance=Money(100)))

    with pytest.raises(PaymentError):
        service.pay_order(1, Money(40))


def test_pay_order_capture_fail(acc_repo, trx_repo):
    gateway = FakeGateway(authorize_ok=True, capture_ok=False)
    service = PaymentService(acc_repo, trx_repo, gateway)

    acc_repo.save(Account(id=1, owner_id=2, balance=Money(100)))

    with pytest.raises(PaymentError):
        service.pay_order(1, Money(40))


def test_pay_order_insufficient_funds(acc_repo, trx_repo):
    gateway = FakeGateway(authorize_ok=True, capture_ok=True)
    service = PaymentService(acc_repo, trx_repo, gateway)

    acc_repo.save(Account(id=1, owner_id=2, balance=Money(10)))

    with pytest.raises(InsufficientFunds):
        service.pay_order(1, Money(40))


# ---------- REFUND TESTS ----------

def test_refund_success(acc_repo, trx_repo):
    gateway = FakeGateway(refund_ok=True)
    service = PaymentService(acc_repo, trx_repo, gateway)

    acc_repo.save(Account(id=1, owner_id=2, balance=Money(10)))

    trx = service.refund(1, Money(50))
    assert trx.status == TransactionStatus.SUCCESS
    assert acc_repo.get(1).balance.amount == 60


def test_refund_gateway_fail(acc_repo, trx_repo):
    gateway = FakeGateway(refund_ok=False)
    service = PaymentService(acc_repo, trx_repo, gateway)

    acc_repo.save(Account(id=1, owner_id=2, balance=Money(10)))

    with pytest.raises(PaymentError):
        service.refund(1, Money(50))


# ---------- TRANSACTION FETCH TESTS ----------

def test_get_transaction_success(service, acc_repo, trx_repo):
    acc_repo.save(Account(id=1, owner_id=1, balance=Money(100)))

    trx = service.transfer(1, 1, Money(10))  # self-transfer for test
    fetched = service.get_transaction(trx.id)

    assert fetched.id == trx.id
    assert fetched.status == TransactionStatus.SUCCESS


def test_get_transaction_not_found(service):
    with pytest.raises(TransactionNotFound):
        service.get_transaction(999999)
