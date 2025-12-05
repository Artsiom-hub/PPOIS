import unittest
import datetime

from core.users.models import Customer
from core.payments.models import BankAccount, PaymentCard, Transaction
from core.payments.gateway import PaymentGateway
from core.exceptions.travel_errors import (
    InsufficientFundsError,
    PaymentDeclinedError
)


class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.acc = BankAccount("IBAN1", "Owner", 100)

    def test_deposit(self):
        self.acc.deposit(50)
        self.assertEqual(self.acc.balance, 150)

    def test_deposit_negative(self):
        with self.assertRaises(ValueError):
            self.acc.deposit(-10)

    def test_withdraw_ok(self):
        self.acc.withdraw(40)
        self.assertEqual(self.acc.balance, 60)

    def test_withdraw_insufficient(self):
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(200)


class TestPaymentCard(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.acc = BankAccount("IB1", "Test", 300)
        self.card = PaymentCard(
            card_number="1234",
            owner=self.customer,
            bank_account=self.acc,
            cvv="111",
            expiry_month=12,
            expiry_year=datetime.date.today().year + 1
        )

    def test_card_valid(self):
        self.assertTrue(self.card.is_valid())

    def test_card_expired(self):
        expired = PaymentCard(
            card_number="1111",
            owner=self.customer,
            bank_account=self.acc,
            cvv="222",
            expiry_month=1,
            expiry_year=2000
        )
        self.assertFalse(expired.is_valid())

    def test_charge_success(self):
        self.card.charge(100)
        self.assertEqual(self.acc.balance, 200)

    def test_charge_expired(self):
        expired = PaymentCard(
            card_number="1111",
            owner=self.customer,
            bank_account=self.acc,
            cvv="111",
            expiry_month=1,
            expiry_year=2000
        )
        with self.assertRaises(PaymentDeclinedError):
            expired.charge(50)

    def test_refund(self):
        self.card.refund(50)
        self.assertEqual(self.acc.balance, 350)


class TestPaymentGateway(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.acc1 = BankAccount("IB1", "owner1", 200)
        self.acc2 = BankAccount("IB2", "owner2", 100)

        self.card1 = PaymentCard("111", self.customer, self.acc1, "111", 12, 2050)
        self.card2 = PaymentCard("222", self.customer, self.acc2, "222", 12, 2050)

        self.gateway = PaymentGateway("GATE")

    def test_successful_transfer(self):
        tx = self.gateway.transfer(self.card1, self.card2, 50)
        self.assertEqual(tx.status, "SUCCESS")
        self.assertEqual(self.acc1.balance, 150)
        self.assertEqual(self.acc2.balance, 150)

    def test_transfer_insufficient_funds(self):
        with self.assertRaises(InsufficientFundsError):
            self.gateway.transfer(self.card1, self.card2, 500)
        last_tx = list(self.gateway.transactions.values())[-1]
        self.assertEqual(last_tx.status, "FAILED")

    def test_get_transaction(self):
        tx = self.gateway.transfer(self.card1, self.card2, 10)
        fetched = self.gateway.get_transaction(tx.tx_id)
        self.assertEqual(fetched, tx)
