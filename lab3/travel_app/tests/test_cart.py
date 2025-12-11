import unittest

from core.cart.cart import Cart
from core.cart.items import CartItem
from core.users.models import Customer


class TestCart(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.cart = Cart(self.customer)

    def test_add_item(self):
        item = CartItem("TEST", None, 50)
        self.cart.add_item(item)
        self.assertEqual(len(self.cart.items), 1)

    def test_total(self):
        self.cart.add_item(CartItem("A", None, 30, quantity=2))
        self.cart.add_item(CartItem("B", None, 40))
        self.assertEqual(self.cart.total(), 100)

    def test_clear(self):
        self.cart.add_item(CartItem("A", None, 30))
        self.cart.clear()
        self.assertEqual(self.cart.items, [])
