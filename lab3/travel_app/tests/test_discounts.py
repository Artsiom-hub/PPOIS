import unittest
import datetime

from core.discounts.coupons import Coupon
from core.discounts.discounts import Discount
from core.exceptions.travel_errors import CouponExpiredError


class TestCoupon(unittest.TestCase):
    def test_apply_valid(self):
        c = Coupon("C10", 10, datetime.datetime.utcnow() + datetime.timedelta(days=1))
        result = c.apply(100)
        self.assertEqual(result, 90)

    def test_expired(self):
        c = Coupon("C10", 10, datetime.datetime.utcnow() - datetime.timedelta(days=1))
        with self.assertRaises(CouponExpiredError):
            c.apply(100)

    def test_used(self):
        c = Coupon("C10", 10, datetime.datetime.utcnow() + datetime.timedelta(days=1))
        c.apply(100)
        with self.assertRaises(CouponExpiredError):
            c.apply(50)


class TestDiscount(unittest.TestCase):
    def test_discount_apply(self):
        d = Discount("Mega", 20, 100)
        self.assertEqual(d.apply_if_applicable(150), 120)

    def test_discount_not_applied(self):
        d = Discount("Mega", 20, 100)
        self.assertEqual(d.apply_if_applicable(90), 90)
