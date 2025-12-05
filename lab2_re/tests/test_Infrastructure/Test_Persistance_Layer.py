# lab2re/Unit_tests/test_Infrastructure/Test_Persistance_Layer.py

import pytest

# ============================================================
#                   BOOK REPOSITORY TESTS
# ============================================================

from Infrastructure.Persistence_Layer.in_memory.book_repo import InMemoryBookRepository  # :contentReference[oaicite:5]{index=5}
from Core_Domains.book_catalog.models import Book
from Core_Domains.book_catalog.value_objects import Price
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Infrastructure.Persistence_Layer.sqlite.db import Base

def test_book_repo_save_and_get():
    repo = InMemoryBookRepository()
    book = Book(id=1, title="Test", authors=[], genre=None, publisher=None,
                edition=None, price=Price(10))

    repo.save(book)
    assert repo.get(1).title == "Test"


def test_book_repo_list():
    repo = InMemoryBookRepository()

    repo.save(Book(id=1, title="A", authors=[], genre=None, publisher=None,
                   edition=None, price=Price(10)))
    repo.save(Book(id=2, title="B", authors=[], genre=None, publisher=None,
                   edition=None, price=Price(20)))

    assert len(repo.list()) == 2


def test_book_repo_find_by_title():
    repo = InMemoryBookRepository()

    repo.save(Book(id=1, title="Clean Code", authors=[], genre=None,
                   publisher=None, edition=None, price=Price(10)))
    repo.save(Book(id=2, title="Dirty Code", authors=[], genre=None,
                   publisher=None, edition=None, price=Price(20)))

    res = repo.find_by_title("clean")
    assert len(res) == 1
    assert res[0].id == 1


def test_book_repo_delete():
    repo = InMemoryBookRepository()
    book = Book(id=1, title="X", authors=[], genre=None, publisher=None,
                edition=None, price=Price(10))

    repo.save(book)
    repo.delete(1)

    with pytest.raises(KeyError):
        repo.get(1)



# ============================================================
#                   ORDER REPOSITORY TESTS
# ============================================================

from Infrastructure.Persistence_Layer.in_memory.order_repo import InMemoryOrderRepository  # :contentReference[oaicite:6]{index=6}
from Core_Domains.Order_Processing.models import Order
from Core_Domains.Order_Processing.value_objects import OrderStatus


def test_order_repo_save_and_get():
    repo = InMemoryOrderRepository()
    order = Order(id=1, customer_id=10)

    repo.save(order)
    assert repo.get(1).customer_id == 10


def test_order_repo_delete():
    repo = InMemoryOrderRepository()
    order = Order(id=1, customer_id=10)
    repo.save(order)

    repo.delete(1)
    with pytest.raises(KeyError):
        repo.get(1)


def test_order_repo_list_by_customer():
    repo = InMemoryOrderRepository()
    repo.save(Order(id=1, customer_id=5))
    repo.save(Order(id=2, customer_id=5))
    repo.save(Order(id=3, customer_id=7))

    res = repo.list_by_customer(5)
    assert len(res) == 2
    assert all(o.customer_id == 5 for o in res)


def test_order_repo_list_all():
    repo = InMemoryOrderRepository()
    repo.save(Order(id=1, customer_id=1))
    repo.save(Order(id=2, customer_id=1))

    assert len(repo.list_all()) == 2


def test_order_repo_list_by_user():
    repo = InMemoryOrderRepository()
    repo.save(Order(id=1, customer_id=10))
    repo.save(Order(id=2, customer_id=10))
    repo.save(Order(id=3, customer_id=20))

    assert len(repo.list_by_user(10)) == 2


def test_order_repo_find_open_cart():
    repo = InMemoryOrderRepository()

    o1 = Order(id=1, customer_id=7)
    o2 = Order(id=2, customer_id=7)
    o3 = Order(id=3, customer_id=7)

    o1.update_status(OrderStatus.COMPLETED)
    o2.update_status(OrderStatus.CREATED)
    o3.update_status(OrderStatus.PENDING)

    repo.save(o1)
    repo.save(o2)
    repo.save(o3)

    cart = repo.find_open_cart(7)
    assert cart.id == 2 or cart.id == 3



# ============================================================
#                   PAYMENTS REPOSITORY TESTS
# ============================================================

from Infrastructure.Persistence_Layer.in_memory.payments_repo import (     # :contentReference[oaicite:7]{index=7}
    InMemoryAccountRepository,
    InMemoryTransactionRepository
)
from Core_Domains.Payments.models import Account, Transaction
from Core_Domains.Payments.value_objects import Money, TransactionType, TransactionStatus


def test_account_repo_save_and_get():
    repo = InMemoryAccountRepository()
    acc = Account(id=1, owner_id=5, balance=Money(100))

    repo.save(acc)
    loaded = repo.get(1)

    assert loaded.owner_id == 5
    assert loaded.balance.amount == 100


def test_transaction_repo_save_and_get():
    repo = InMemoryTransactionRepository()
    trx = Transaction(id=10, from_account=1, to_account=2,
                      amount=Money(50),
                      type=TransactionType.TRANSFER,
                      status=TransactionStatus.SUCCESS)

    repo.save(trx)
    assert repo.get(10).amount.amount == 50


def test_transaction_repo_list_by_account():
    repo = InMemoryTransactionRepository()

    repo.save(Transaction(id=1, from_account=1, to_account=2,
                          amount=Money(10),
                          type=TransactionType.TRANSFER,
                          status=TransactionStatus.SUCCESS))

    repo.save(Transaction(id=2, from_account=3, to_account=1,
                          amount=Money(20),
                          type=TransactionType.TRANSFER,
                          status=TransactionStatus.SUCCESS))

    res = repo.list_by_account(1)
    assert len(res) == 2



# ============================================================
#                   USER REPOSITORY TESTS
# ============================================================

from Infrastructure.Persistence_Layer.in_memory.user_repo import (          # :contentReference[oaicite:8]{index=8}
    InMemoryUserRepository,
    InMemoryRoleRepository,
    InMemoryPermissionRepository
)
from Core_Domains.User_Security.models import User, Role, Permission


def test_user_repo_save_get():
    repo = InMemoryUserRepository()
    u = User(id=1, email="a@b.c", password_hash="xxx")

    repo.save(u)
    assert repo.get(1).email == "a@b.c"


def test_user_repo_get_by_email():
    repo = InMemoryUserRepository()
    u = User(id=1, email="user@mail.com", password_hash="abc")

    repo.save(u)
    assert repo.get_by_email("user@mail.com").id == 1


def test_role_repo_save_get_list():
    repo = InMemoryRoleRepository()
    r1 = Role(id=1, name="admin")
    r2 = Role(id=2, name="user")

    repo.save(r1)
    repo.save(r2)

    assert repo.get(1).name == "admin"
    assert len(repo.list()) == 2


def test_permission_repo_save_get_list():
    repo = InMemoryPermissionRepository()
    p1 = Permission(id=1, name="perm1")
    p2 = Permission(id=2, name="perm2")

    repo.save(p1)
    repo.save(p2)

    assert repo.get(1).name == "perm1"
    assert len(repo.list()) == 2
# ============================================================
#        SQLITE PERSISTENCE LAYER — TESTS
# ============================================================

# ============================================================
#           FIXTURE: ИНИЦИАЛИЗАЦИЯ ВРЕМЕННОЙ БАЗЫ
# ============================================================

@pytest.fixture
def sqlite_session():
    """
    Создаём временную in-memory SQLite БД
    и пробрасываем в репозитории через SessionLocal override.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    # возвращаем session factory
    return TestingSession


# ============================================================
#                   BOOK REPO (SQLite)
# ============================================================

def test_sqlite_book_repo_save_get(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.book_repo import (
        SQLiteBookRepository, BookRecord
    )  # :contentReference[oaicite:6]{index=6}
    from Core_Domains.book_catalog.models import Book
    from Core_Domains.book_catalog.value_objects import Price

    # patch SessionLocal → наш in-memory
    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.book_repo.SessionLocal", sqlite_session)

    repo = SQLiteBookRepository()

    book = Book(id=1, title="SQLite Test", authors=[], genre=None,
                publisher=None, edition=None, price=Price(99))

    repo.save(book)
    loaded = repo.get(1)

    assert loaded.title == "SQLite Test"
    assert loaded.price.amount == 99


def test_sqlite_book_repo_list(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.book_repo import SQLiteBookRepository
    from Core_Domains.book_catalog.models import Book
    from Core_Domains.book_catalog.value_objects import Price

    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.book_repo.SessionLocal", sqlite_session)

    repo = SQLiteBookRepository()

    repo.save(Book(id=1, title="A", authors=[], genre=None,
                   publisher=None, edition=None, price=Price(10)))
    repo.save(Book(id=2, title="B", authors=[], genre=None,
                   publisher=None, edition=None, price=Price(20)))

    assert len(repo.list()) == 2


def test_sqlite_book_repo_delete(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.book_repo import SQLiteBookRepository
    from Core_Domains.book_catalog.models import Book
    from Core_Domains.book_catalog.value_objects import Price

    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.book_repo.SessionLocal", sqlite_session)

    repo = SQLiteBookRepository()

    repo.save(Book(id=1, title="X", authors=[], genre=None,
                   publisher=None, edition=None, price=Price(10)))

    repo.delete(1)

    with pytest.raises(KeyError):
        repo.get(1)


# ============================================================
#                   ORDER REPO (SQLite)
# ============================================================

def test_sqlite_order_repo(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.order_repo import SQLiteOrderRepository  # :contentReference[oaicite:7]{index=7}
    from Core_Domains.Order_Processing.models import Order

    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.order_repo.SessionLocal", sqlite_session)

    repo = SQLiteOrderRepository()

    repo.save(Order(id=1, customer_id=5))
    repo.save(Order(id=2, customer_id=5))
    repo.save(Order(id=3, customer_id=7))

    o = repo.get(1)
    assert o.customer_id == 5

    assert len(repo.list_by_customer(5)) == 2

    repo.delete(1)
    with pytest.raises(KeyError):
        repo.get(1)


# ============================================================
#                   PAYMENTS REPO (SQLite)
# ============================================================

def test_sqlite_account_repo(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.payments_repo import SQLiteAccountRepository  # :contentReference[oaicite:8]{index=8}
    from Core_Domains.Payments.models import Account
    from Core_Domains.Payments.value_objects import Money

    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.payments_repo.SessionLocal", sqlite_session)

    repo = SQLiteAccountRepository()

    acc = Account(id=10, owner_id=99, balance=Money(150))
    repo.save(acc)

    loaded = repo.get(10)
    assert loaded.owner_id == 99
    assert loaded.balance.amount == 150


def test_sqlite_transaction_repo(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.payments_repo import SQLiteTransactionRepository
    from Core_Domains.Payments.models import Transaction
    from Core_Domains.Payments.value_objects import Money, TransactionType, TransactionStatus

    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.payments_repo.SessionLocal", sqlite_session)

    repo = SQLiteTransactionRepository()

    trx = Transaction(
        id=1,
        from_account=10,
        to_account=20,
        amount=Money(30),
        type=TransactionType.TRANSFER,
        status=TransactionStatus.SUCCESS,
    )

    repo.save(trx)

    loaded = repo.get(1)
    assert loaded.amount.amount == 30
    assert loaded.status == TransactionStatus.SUCCESS


# ============================================================
#                   USER REPO (SQLite)
# ============================================================

def test_sqlite_user_repo(sqlite_session, monkeypatch):
    from Infrastructure.Persistence_Layer.sqlite.user_repo import SQLiteUserRepository  # :contentReference[oaicite:9]{index=9}
    from Core_Domains.User_Security.models import User

    monkeypatch.setattr("Infrastructure.Persistence_Layer.sqlite.user_repo.SessionLocal", sqlite_session)

    repo = SQLiteUserRepository()

    user = User(id=1, email="x@y.com", password_hash="hashed")
    repo.save(user)

    loaded = repo.get(1)
    assert loaded.email == "x@y.com"
    assert repo.get_by_email("x@y.com").id == 1

    repo.save(User(id=1, email="updated@mail.com", password_hash="h2"))
    assert repo.get(1).email == "updated@mail.com"





