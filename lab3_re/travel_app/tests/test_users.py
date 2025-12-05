import unittest
import hashlib
import datetime

from core.users.models import User, Customer, TravelAgent
from core.payments.models import BankAccount, PaymentCard
from core.exceptions.travel_errors import CardNotFoundError


class TestUser(unittest.TestCase):
    def setUp(self):
        self.raw_password = "secret123"
        self.hashed = hashlib.sha256(self.raw_password.encode()).hexdigest()
        self.user = User(
            user_id="u1",
            email="test@example.com",
            password_hash=self.hashed
        )

    def test_password_correct(self):
        self.assertTrue(self.user.check_password("secret123"))

    def test_password_incorrect(self):
        self.assertFalse(self.user.check_password("wrongpass"))

    def test_user_deactivate(self):
        self.user.deactivate()
        self.assertFalse(self.user.active)


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(
            user_id="c1",
            email="cust@example.com",
            password_hash="hash",
            full_name="John Doe"
        )

    def test_add_card(self):
        acc = BankAccount("IB1", "John Doe", 500)
        card = PaymentCard(
            card_number="1234",
            owner=self.customer,
            bank_account=acc,
            cvv="123",
            expiry_month=12,
            expiry_year=2050
        )
        self.customer.add_card(card)
        self.assertEqual(self.customer.cards[0], card)

    def test_get_default_card_no_cards(self):
        with self.assertRaises(CardNotFoundError):
            self.customer.get_default_card()


class DummyBooking:
    def __init__(self, price):
        self.total_price = price


class TestTravelAgent(unittest.TestCase):
    def setUp(self):
        self.agent = TravelAgent(
            user_id="a1",
            email="agent@example.com",
            password_hash="hash",
            agency_name="BestTravel",
            commission_rate=0.1
        )

    def test_register_booking(self):
        booking = DummyBooking(100)
        self.agent.register_booking(booking)
        self.assertEqual(self.agent.managed_bookings[0], booking)

    def test_calculate_commission(self):
        booking = DummyBooking(200)
        self.assertEqual(self.agent.calculate_commission(booking), 20.0)
