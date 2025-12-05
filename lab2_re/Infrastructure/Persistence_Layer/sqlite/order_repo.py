# Infrastructure/persistence/sqlite/order_repo.py

from sqlalchemy import Column, Integer
from sqlalchemy.orm import Session
from Infrastructure.Persistence_Layer.sqlite.db import Base, SessionLocal
from Core_Domains.Order_Processing.models import Order
from Core_Domains.Order_Processing.repository_interface import OrderRepository


class OrderRecord(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)


class SQLiteOrderRepository(OrderRepository):
    def __init__(self):
        self.db: Session = SessionLocal()
        Base.metadata.create_all(bind=self.db.bind)
    def get(self, order_id: int) -> Order:
        rec = self.db.query(OrderRecord).filter(OrderRecord.id == order_id).first()
        if not rec:
            raise KeyError(order_id)

        # минимальная доменная модель
        return Order(id=rec.id, customer_id=rec.customer_id)

    def save(self, order: Order):
        rec = self.db.query(OrderRecord).filter(OrderRecord.id == order.id).first()

        if not rec:
            rec = OrderRecord(id=order.id)

        rec.customer_id = order.customer_id
        self.db.add(rec)
        self.db.commit()

    def list_by_customer(self, customer_id: int):
        return [
            Order(id=r.id, customer_id=r.customer_id)
            for r in self.db.query(OrderRecord)
            .filter(OrderRecord.customer_id == customer_id)
            .all()
        ]

    def delete(self, order_id: int):
        rec = self.db.query(OrderRecord).filter(OrderRecord.id == order_id).first()
        if rec:
            self.db.delete(rec)
            self.db.commit()
