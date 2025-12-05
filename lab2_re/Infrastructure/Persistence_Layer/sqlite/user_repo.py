from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from Infrastructure.Persistence_Layer.sqlite.db import Base, SessionLocal
from Core_Domains.User_Security.models import User
from Core_Domains.User_Security.repository_interface import UserRepository


class UserRecord(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)


class SQLiteUserRepository(UserRepository):

    def __init__(self):
        self.db: Session = SessionLocal()
        Base.metadata.create_all(bind=self.db.bind)

    # === REQUIRED BY INTERFACE ===
    def get(self, user_id: int):
        rec = self.db.query(UserRecord).filter(UserRecord.id == user_id).first()
        if not rec:
            raise KeyError(user_id)
        return User(id=rec.id, email=rec.email, password_hash=rec.password_hash)

    def get_by_email(self, email: str):
        rec = self.db.query(UserRecord).filter(UserRecord.email == email).first()
        if rec:
            return User(id=rec.id, email=rec.email, password_hash=rec.password_hash)
        return None

    def save(self, user: User):
        rec = self.db.query(UserRecord).filter(UserRecord.id == user.id).first()
        if not rec:
            rec = UserRecord(id=user.id)

        rec.email = user.email
        rec.password_hash = user.password_hash

        self.db.add(rec)
        self.db.commit()

    # === EXTRA METHODS REQUIRED BY TESTS ===
    def delete(self, user_id: int):
        rec = self.db.query(UserRecord).filter(UserRecord.id == user_id).first()
        if rec:
            self.db.delete(rec)
            self.db.commit()
        else:
            raise KeyError(user_id)

    def list(self):
        rows = self.db.query(UserRecord).all()
        return [
            User(id=r.id, email=r.email, password_hash=r.password_hash)
            for r in rows
        ]

    def clear(self):
        self.db.query(UserRecord).delete()
        self.db.commit()
