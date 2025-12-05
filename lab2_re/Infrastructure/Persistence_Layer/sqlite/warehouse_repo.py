from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from datetime import datetime

# ВАЖНО: Base общая для всех таблиц
Base = declarative_base()

# SessionLocal будет заменён monkeypatch в тестах
SessionLocal = sessionmaker()

# =====================================================================
#  MODELS (SQLAlchemy)
# =====================================================================

class CellRecord(Base):
    __tablename__ = "warehouse_cells"

    id = Column(Integer, primary_key=True)
    shelf_id = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    description = Column(String)


class StockRecord(Base):
    __tablename__ = "warehouse_stock"

    id = Column(Integer, primary_key=True)
    cell_id = Column(Integer, ForeignKey("warehouse_cells.id"), nullable=False)
    book_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

    cell = relationship("CellRecord")


class StockMovementRecord(Base):
    __tablename__ = "warehouse_stock_movements"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("warehouse_stock.id"), nullable=False)
    delta = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockRecord")


class InventorySessionRecord(Base):
    __tablename__ = "warehouse_inventory_sessions"

    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)


# =====================================================================
#  Таблицы создаются корректно для каждого engine
# =====================================================================

_prev_engine = None

def _ensure_tables():
    """
    Тесты создают новый engine через фикстуру sqlite_session.
    Monkeypatch подменяет SessionLocal на новый sessionmaker(bind=new_engine).

    SQLAlchemy Base.metadata.create_all уже была вызвана для другого engine,
    поэтому для нового — нужно пересоздать таблицы вручную.
    """
    global _prev_engine

    # достаём текущий engine
    session = SessionLocal()
    engine = session.bind

    # engine мог быть None: тесты иногда создают "чистую" sessionmaker
    if engine is None:
        return

    # если engine новый → пересоздаём все таблицы
    if engine is not _prev_engine:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        _prev_engine = engine


# =====================================================================
#  REPOSITORIES
# =====================================================================

class SQLiteStockRepository:
    def __init__(self):
        _ensure_tables()
        self.db: Session = SessionLocal()

    def get(self, stock_id: int):
        return self.db.query(StockRecord).filter_by(id=stock_id).first()

    def save(self, stock: StockRecord):
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock


class SQLiteStockMovementRepository:
    def __init__(self):
        _ensure_tables()
        self.db: Session = SessionLocal()

    def save(self, movement: StockMovementRecord):
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def list_for_stock(self, stock_id: int):
        return self.db.query(StockMovementRecord).filter_by(stock_id=stock_id).all()


class SQLiteInventorySessionRepository:
    def __init__(self):
        _ensure_tables()
        self.db: Session = SessionLocal()

    def save(self, inv: InventorySessionRecord):
        self.db.add(inv)
        self.db.commit()
        self.db.refresh(inv)
        return inv

    def get(self, session_id: int):
        return self.db.query(InventorySessionRecord).filter_by(id=session_id).first()
