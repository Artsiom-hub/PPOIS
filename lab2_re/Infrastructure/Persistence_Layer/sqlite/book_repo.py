# Infrastructure/persistence/sqlite/book_repo.py

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session

from Infrastructure.Persistence_Layer.sqlite.db import Base, SessionLocal, engine
from Core_Domains.book_catalog.models import Book
from Core_Domains.book_catalog.repository_interface import BookRepository
from Core_Domains.book_catalog.value_objects import Price


class BookRecord(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Float)


        
class SQLiteBookRepository(BookRepository):

    def __init__(self):
        self.db: Session = SessionLocal()
        Base.metadata.create_all(bind=self.db.bind)

    def get(self, book_id: int) -> Book:
        rec = self.db.query(BookRecord).filter(BookRecord.id == book_id).first()
        if not rec:
            raise KeyError(book_id)

        # минимальная конвертация обратно в доменную модель
        return Book(
            id=rec.id,
            title=rec.title,
            authors=[],
            genre=None,
            publisher=None,
            edition=None,
            price=Price(rec.price),
        )

    def save(self, book: Book):
        rec = self.db.query(BookRecord).filter(BookRecord.id == book.id).first()

        if not rec:
            rec = BookRecord(id=book.id)

        rec.title = book.title
        rec.price = book.price.amount

        self.db.add(rec)
        self.db.commit()

    def delete(self, book_id: int):
        rec = self.db.query(BookRecord).filter(BookRecord.id == book_id).first()
        if rec:
            self.db.delete(rec)
            self.db.commit()

    def list(self):
        return [
            Book(
                id=r.id,
                title=r.title,
                authors=[],
                genre=None,
                publisher=None,
                edition=None,
                price=Price(r.price),
            )
            for r in self.db.query(BookRecord).all()
        ]

    def find_by_title(self, title: str):
        return [
            Book(
                id=r.id,
                title=r.title,
                authors=[],
                genre=None,
                publisher=None,
                edition=None,
                price=Price(r.price),
            )
            for r in self.db.query(BookRecord)
            .filter(BookRecord.title.ilike(f"%{title}%"))
            .all()
        ]


