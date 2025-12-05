import pytest
from Core_Domains.Payments.services import PaymentService
from Core_Domains.Payments.value_objects import Money, TransactionType, TransactionStatus
from Core_Domains.Payments.models import Account, Transaction
from Core_Domains.Payments.exceptions import AccountNotFound, InsufficientFunds, PaymentError

class AccRepo:
    def __init__(self): self.data={}
    def get(self,id):
        if id not in self.data: raise KeyError
        return self.data[id]
    def save(self,a): self.data[a.id]=a

class TrxRepo:
    def __init__(self): self.data={}
    def get(self,id):
        if id not in self.data: raise KeyError
        return self.data[id]
    def save(self,t): self.data[t.id]=t

class FakeGateway:
    def __init__(self,ok=True): self.ok=ok
    def authorize(self,a): return self.ok
    def capture(self,a): return self.ok
    def refund(self,a): return self.ok

@pytest.fixture
def svc():
    a=AccRepo(); t=TrxRepo()
    a.save(Account(id=1, owner_id=1, balance=Money(100)))
    a.save(Account(id=2, owner_id=2, balance=Money(50)))
    return PaymentService(a,t,FakeGateway(ok=True))

def test_transfer(svc):
    trx=svc.transfer(1,2,Money(20))
    assert trx.status==TransactionStatus.SUCCESS

def test_transfer_not_found(svc):
    with pytest.raises(AccountNotFound):
        svc.transfer(99,1,Money(10))

def test_transfer_insufficient(svc):
    with pytest.raises(InsufficientFunds):
        svc.transfer(2,1,Money(999))

def test_pay_order(svc):
    trx=svc.pay_order(1,Money(10))
    assert trx.status==TransactionStatus.SUCCESS

def test_pay_order_capture_fail():
    svc=PaymentService(AccRepo(),TrxRepo(),FakeGateway(ok=False))
    svc.account_repo.save(Account(id=1,owner_id=1,balance=Money(100)))
    with pytest.raises(PaymentError):
        svc.pay_order(1,Money(10))

def test_refund(svc):
    trx=svc.refund(1,Money(30))
    assert trx.status==TransactionStatus.SUCCESS
