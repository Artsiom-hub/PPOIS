# lab2re/Unit_tests/test_Infrastructure/Test_api.py

import pytest
from fastapi.testclient import TestClient

from Infrastructure.api.main import app


client = TestClient(app)


# ============================================================
#                     BOOKS API TESTS
# ============================================================

def test_search_books_empty():
    """
    Проверяем корректный ответ при пустом каталоге.
    """
    resp = client.post("/books/search", json={"title": "anything"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_books_found(monkeypatch):
    """
    Патчим сервис, чтобы гарантировать конкретный ответ.
    """
    from Infrastructure.api.dependencies import get_book_service

    service = get_book_service()

    # добавляем одну книгу вручную
    from Core_Domains.book_catalog.models import Book, Author, Genre, Publisher, Edition
    from Core_Domains.book_catalog.value_objects import Price
    from datetime import date

    service.add_book(
        Book(
            id=1,
            title="Clean Code",
            authors=[Author(1, "Robert Martin")],
            genre=Genre(1, "Programming"),
            publisher=Publisher(1, "PH"),
            edition=Edition("ISBN1", date.today(), 200),
            price=Price(40),
        )
    )

    resp = client.post("/books/search", json={"title": "clean"})
    assert resp.status_code == 200
    assert resp.json() == ["Clean Code"]


# ============================================================
#                     USERS API TESTS
# ============================================================

def test_user_register():
    resp = client.post("/users/register", json={
        "email": "test@test.com",
        "password": "123"
    })

    assert resp.status_code == 200
    data = resp.json()
    assert "user_id" in data


def test_user_login_success():
    client.post("/users/register", json={
        "email": "login@test.com",
        "password": "1234"
    })

    resp = client.post("/users/login", json={
        "email": "login@test.com",
        "password": "1234"
    })

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"




# ============================================================
#                     ORDERS API TESTS
# ============================================================

def test_create_order():
    resp = client.post("/orders/create", json={"customer_id": 1})
    assert resp.status_code == 200
    assert "order_id" in resp.json()


def test_add_book_to_order():
    # Создаём заказ
    order_id = client.post("/orders/create", json={"customer_id": 10}).json()["order_id"]

    # Добавляем книгу заранее в BookService
    from Infrastructure.api.dependencies import get_book_service
    book_service = get_book_service()

    from Core_Domains.book_catalog.models import Book, Author, Genre, Publisher, Edition
    from Core_Domains.book_catalog.value_objects import Price
    from datetime import date

    book_service.add_book(
        Book(
            id=5,
            title="Testing Book",
            authors=[Author(1, "Tester")],
            genre=Genre(1, "QA"),
            publisher=Publisher(1, "Pub"),
            edition=Edition("ISBN5", date.today(), 100),
            price=Price(20),
        )
    )

    resp = client.post(f"/orders/{order_id}/add-book", json={
        "book_id": 5,
        "qty": 2
    })

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_order_pay_success():
    # Заводим заказ
    order_id = client.post("/orders/create", json={"customer_id": 1}).json()["order_id"]

    # Добавляем книгу
    from Infrastructure.api.dependencies import get_book_service
    svc = get_book_service()

    from Core_Domains.book_catalog.models import Book, Author, Genre, Publisher, Edition
    from Core_Domains.book_catalog.value_objects import Price
    from datetime import date

    svc.add_book(
        Book(
            id=999,
            title="Payable",
            authors=[Author(1, "A")],
            genre=Genre(1, "G"),
            publisher=Publisher(1, "P"),
            edition=Edition("I", date.today(), 10),
            price=Price(5)
        )
    )

    client.post(f"/orders/{order_id}/add-book", json={"book_id": 999, "qty": 1})

    # Оплачиваем
    resp = client.post(f"/orders/{order_id}/pay")
    assert resp.status_code == 200
    assert resp.json()["status"] == "paid"




# ============================================================
#                     WAREHOUSE API TESTS
# ============================================================

def test_warehouse_inbound():
    # добавляем ячейку вручную в cell_repo
    from Infrastructure.api.dependencies import cell_repo
    from Core_Domains.Warehouse.models import Cell

    cell_repo.save(Cell(id=10, shelf_id=1, code="A-10", capacity=100))

    resp = client.post("/warehouse/inbound", json={
        "book_id": 1,
        "cell_id": 10,
        "qty": 5
    })

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_warehouse_relocate():
    from Infrastructure.api.dependencies import cell_repo, stock_repo
    from Core_Domains.Warehouse.models import Cell, StockItem
    from Core_Domains.Warehouse.value_objects import Quantity

    # две ячейки
    cell_repo.save(Cell(id=1, shelf_id=1, code="A1", capacity=100))
    cell_repo.save(Cell(id=2, shelf_id=1, code="A2", capacity=100))

    # исходный складской остаток
    stock_repo.save(StockItem(book_id=5, cell_id=1, quantity=Quantity(10)))

    resp = client.post("/warehouse/relocate", json={
        "book_id": 5,
        "from_cell": 1,
        "to_cell": 2,
        "qty": 3
    })

    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
