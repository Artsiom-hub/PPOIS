# lab2re/Unit_tests/test_Infrastructure/Test_integrations.py

import pytest
import logging


# ======================================================================
#                         TEST ExternalBookApi
# ======================================================================

def test_external_book_api_success(monkeypatch):
    """
    Проверяем успешное получение данных по ISBN.
    """

    from Infrastructure.integrations.books.external_book_api import ExternalBookApi

    # подмена requests.get
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "totalItems": 1,
                "items": [
                    {
                        "volumeInfo": {
                            "title": "Test Book",
                            "authors": ["Author A"],
                            "publisher": "Publisher X",
                            "publishedDate": "2020-01-01",
                            "description": "Some description"
                        }
                    }
                ]
            }

    def fake_get(url, params):
        return FakeResponse()

    monkeypatch.setattr("Infrastructure.integrations.books.external_book_api.requests.get", fake_get)

    api = ExternalBookApi()
    result = api.find_by_isbn("12345")

    assert result["title"] == "Test Book"
    assert result["authors"] == ["Author A"]


def test_external_book_api_not_found(monkeypatch):
    from Infrastructure.integrations.books.external_book_api import ExternalBookApi

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"totalItems": 0}

    monkeypatch.setattr("Infrastructure.integrations.books.external_book_api.requests.get", lambda *a, **k: FakeResponse())

    api = ExternalBookApi()
    assert api.find_by_isbn("nope") is None


def test_external_book_api_bad_status(monkeypatch):
    from Infrastructure.integrations.books.external_book_api import ExternalBookApi

    class FakeResponse:
        status_code = 500

    monkeypatch.setattr("Infrastructure.integrations.books.external_book_api.requests.get", lambda *a, **k: FakeResponse())

    api = ExternalBookApi()
    assert api.find_by_isbn("xxx") is None







# ======================================================================
#                         TEST AuditLogger
# ======================================================================

def test_audit_logger(caplog):
    """
    Проверяем, что AuditLogger пишет корректные сообщения.
    """

    from Infrastructure.integrations.logging.audit_logger import AuditLogger

    caplog.set_level(logging.INFO, logger="audit")

    logger = AuditLogger()
    logger.log_user_login(123)
    logger.log_order_created(55)
    logger.log_stock_movement(10, 1, 2, 5)

    logs = [rec.message for rec in caplog.records]

    assert "User login: 123" in logs
    assert "Order created: 55" in logs
    assert "book=10, from=1, to=2, qty=5" in logs[-1]





# ======================================================================
#                         TEST BankGateway
# ======================================================================

def test_bank_gateway_authorize(monkeypatch):
    """
    Проверяем метод authorize_payment – подменяем random.random.
    """

    from Infrastructure.integrations.payments.bank_gateway import BankGateway

    monkeypatch.setattr("Infrastructure.integrations.payments.bank_gateway.random.random", lambda: 0.99)
    assert BankGateway().authorize_payment(100) is True

    monkeypatch.setattr("Infrastructure.integrations.payments.bank_gateway.random.random", lambda: 0.01)
    assert BankGateway().authorize_payment(100) is False


def test_bank_gateway_transaction_status():
    """
    Проверяем возврат статуса транзакции.
    """

    from Infrastructure.integrations.payments.bank_gateway import BankGateway
    from Core_Domains.Payments.value_objects import TransactionStatus

    gw = BankGateway()
    assert gw.get_transaction_status("xxx") == TransactionStatus.SUCCESS
