# Infrastructure/persistence/sqlite/payments_repo.py

from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import Session

from Infrastructure.Persistence_Layer.sqlite.db import Base, SessionLocal
from Core_Domains.Payments.repository_interface import (
    AccountRepository, TransactionRepository
)
from Core_Domains.Payments.models import Account, Transaction
from Core_Domains.Payments.value_objects import Money, TransactionType, TransactionStatus


class AccountRecord(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer)
    balance = Column(Float)


class TransactionRecord(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    from_account = Column(Integer)
    to_account = Column(Integer)
    amount = Column(Float)
    type = Column(String)
    status = Column(String)


class SQLiteAccountRepository(AccountRepository):
    def __init__(self):
        self.db: Session = SessionLocal()
        Base.metadata.create_all(bind=self.db.bind)

    def get(self, account_id: int):
        rec = self.db.query(AccountRecord).filter(AccountRecord.id == account_id).first()
        if not rec:
            raise KeyError(account_id)
        return Account(
            id=rec.id,
            owner_id=rec.owner_id,
            balance=Money(rec.balance)
        )

    def save(self, account):
        rec = self.db.query(AccountRecord).filter(AccountRecord.id == account.id).first()
        if not rec:
            rec = AccountRecord(id=account.id)

        rec.owner_id = account.owner_id
        rec.balance = account.balance.amount

        self.db.add(rec)
        self.db.commit()


class SQLiteTransactionRepository(TransactionRepository):
    def __init__(self):
        self.db: Session = SessionLocal()
        Base.metadata.create_all(bind=self.db.bind)
    def save(self, trx):
        rec = TransactionRecord(
            id=trx.id,
            from_account=trx.from_account,
            to_account=trx.to_account,
            amount=trx.amount.amount,
            type=trx.type.value,
            status=trx.status.value,
        )
        self.db.add(rec)
        self.db.commit()

    def get(self, trx_id: int):
        rec = self.db.query(TransactionRecord).filter(TransactionRecord.id == trx_id).first()
        if not rec:
            raise KeyError(trx_id)

        return Transaction(
            id=rec.id,
            from_account=rec.from_account,
            to_account=rec.to_account,
            amount=Money(rec.amount),
            type=TransactionType(rec.type),
            status=TransactionStatus(rec.status),
        )
    def list_by_account(self, account_id: int):
        # возвращаем все транзакции, где аккаунт участвует как sender или receiver
        recs = (
            self.db.query(TransactionRecord)
            .filter(
                (TransactionRecord.from_account == account_id)
                | (TransactionRecord.to_account == account_id)
            )
            .all()
        )

        from Core_Domains.Payments.models import Transaction
        from Core_Domains.Payments.value_objects import Money, TransactionType, TransactionStatus

        return [
            Transaction(
                id=r.id,
                from_account=r.from_account,
                to_account=r.to_account,
                amount=Money(r.amount),
                type=TransactionType(r.type),
                status=TransactionStatus(r.status),
            )
            for r in recs
        ]

