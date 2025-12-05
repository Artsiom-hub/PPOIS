import pytest

from Core_Domains.Payments.services import PaymentService              # :contentReference[oaicite:0]{index=0}
from Core_Domains.Payments.models import Account, Transaction
from Core_Domains.Payments.value_objects import Money, TransactionType, TransactionStatus
from Core_Domains.Payments.exceptions import (
    AccountNotFound,
    InsufficientFunds,
    PaymentError
)


# =====================================================================
#                           MOCK REPOSITORIES
# =====================================================================

class AccountRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def save(self, acc):
        self.data[acc.id] = acc


class TransactionRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def save(self, trx):
        self.data[trx.id] = trx


class GatewayMock:
    def __init__(self, authorize_result=True, capture_result=True, refund_result=True):
        self.authorize_result = authorize_result
        self.capture_result = capture_result
        self.refund_result = refund_result

    def authorize(self, amount):
        return self.authorize_result

    def capture(self, amount):
        return self.capture_result

    def refund(self, amount):
        return self.refund_result


# =====================================================================
#                           FIXTURE
# =====================================================================

@pytest.fixture
def svc():
    a = AccountRepoMock()
    t = TransactionRepoMock()

    a.save(Account(id=1, owner_id=10, balance=Money(100)))
    a.save(Account(id=2, owner_id=20, balance=Money(200)))

    gw = GatewayMock()

    return PaymentService(a, t, gw)


# =====================================================================
#                           TESTS
# =====================================================================


# ------------------ TRANSFER TESTS ----------------------

def test_transfer_success(svc):
    trx = svc.transfer(1, 2, Money(50))
    assert trx.status == TransactionStatus.SUCCESS
    assert svc.account_repo.get(1).balance.amount == 50
    assert svc.account_repo.get(2).balance.amount == 250


def test_transfer_account_not_found(svc):
    with pytest.raises(AccountNotFound):
        svc.transfer(999, 2, Money(10))


def test_transfer_to_self(svc):
    with pytest.raises(PaymentError):
        svc.transfer(1, 1, Money(10))


def test_transfer_zero_amount(svc):
    with pytest.raises(PaymentError):
        svc.transfer(1, 2, Money(0))


def test_transfer_insufficient(svc):
    with pytest.raises(InsufficientFunds):
        svc.transfer(1, 2, Money(999))


def test_transfer_gateway_authorize_fail():
    a = AccountRepoMock()
    t = TransactionRepoMock()

    a.save(Account(id=1, owner_id=1, balance=Money(100)))
    a.save(Account(id=2, owner_id=2, balance=Money(100)))

    gw = GatewayMock(authorize_result=False)

    svc = PaymentService(a, t, gw)

    with pytest.raises(PaymentError):
        svc.transfer(1, 2, Money(10))


def test_transfer_gateway_capture_fail():
    a = AccountRepoMock()
    t = TransactionRepoMock()

    a.save(Account(id=1, owner_id=1, balance=Money(100)))
    a.save(Account(id=2, owner_id=2, balance=Money(100)))

    gw = GatewayMock(authorize_result=True, capture_result=False)

    svc = PaymentService(a, t, gw)

    with pytest.raises(PaymentError):
        svc.transfer(1, 2, Money(10))


# ------------------ PAY ORDER ----------------------

def test_pay_order_success(svc):
    trx = svc.pay_order(1, Money(10))
    assert trx.status == TransactionStatus.SUCCESS
    assert svc.account_repo.get(1).balance.amount == 90


def test_pay_order_account_not_found(svc):
    with pytest.raises(AccountNotFound):
        svc.pay_order(999, Money(10))


def test_pay_order_insufficient(svc):
    with pytest.raises(InsufficientFunds):
        svc.pay_order(1, Money(9999))


def test_pay_order_gateway_authorize_fail(svc):
    svc.gateway.authorize_result = False
    with pytest.raises(PaymentError):
        svc.pay_order(1, Money(10))


def test_pay_order_gateway_capture_fail(svc):
    svc.gateway.capture_result = False
    with pytest.raises(PaymentError):
        svc.pay_order(1, Money(10))


# ------------------ REFUND ----------------------

def test_refund_success(svc):
    trx = svc.refund(2, Money(50))
    assert trx.status == TransactionStatus.SUCCESS
    assert svc.account_repo.get(2).balance.amount == 250


def test_refund_account_not_found(svc):
    with pytest.raises(AccountNotFound):
        svc.refund(999, Money(10))


def test_refund_gateway_fail(svc):
    svc.gateway.refund_result = False
    with pytest.raises(PaymentError):
        svc.refund(2, Money(10))


def test_refund_zero(svc):
    with pytest.raises(PaymentError):
        svc.refund(2, Money(0))


# ------------------ INTERNAL: TRANSACTION RECORDING ----------------------

def test_transaction_recorded(svc):
    svc.transfer(1, 2, Money(10))

    # only 1 transaction
    assert len(svc.trx_repo.data.values()) == 1
    trx = list(svc.trx_repo.data.values())[0]

    assert trx.type == TransactionType.TRANSFER
    assert trx.amount.amount == 10
    assert trx.status == TransactionStatus.SUCCESS
