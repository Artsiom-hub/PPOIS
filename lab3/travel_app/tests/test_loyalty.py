import unittest
import datetime

from core.loyalty.program import LoyaltyProgram
from core.loyalty.account import LoyaltyAccount
from core.users.models import Customer
from core.bookings.base import Booking


class TestLoyaltyProgram(unittest.TestCase):
    def setUp(self):
        self.prog = LoyaltyProgram("LP", base_multiplier=2.0)
        self.prog.add_level("SILVER", 100)
        self.prog.add_level("GOLD", 500)

    def test_levels(self):
        self.assertEqual(self.prog.levels["SILVER"], 100)
        self.assertEqual(self.prog.level_for_points(0), "NONE")
        self.assertEqual(self.prog.level_for_points(150), "SILVER")


class TestLoyaltyAccount(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "m", "h")
        self.prog = LoyaltyProgram("LP", base_multiplier=1.0)
        self.account = LoyaltyAccount(self.customer, self.prog)

    def test_add_points(self):
        booking = Booking("b1", self.customer, datetime.datetime.utcnow(), 200)
        self.account.add_points_for_booking(booking)
        self.assertEqual(self.account.points, 200)

    def test_redeem(self):
        self.account.points = 100
        self.account.redeem_points(50)
        self.assertEqual(self.account.points, 50)

    def test_redeem_fail(self):
        with self.assertRaises(Exception):
            self.account.redeem_points(999)
