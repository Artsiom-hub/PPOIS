import unittest

from core.users.models import Customer
from core.support.message import ChatMessage
from core.support.ticket import SupportTicket


class TestChatMessage(unittest.TestCase):
    def test_preview(self):
        user = Customer("c1", "mail", "hash")
        msg = ChatMessage("m1", user, "Hello World")
        self.assertEqual(msg.preview(), "Hello World")


class TestSupportTicket(unittest.TestCase):
    def test_add_message(self):
        user = Customer("c1", "mail", "hash")
        t = SupportTicket("t1", user, "Help")
        msg = ChatMessage("m1", user, "hi")
        t.add_message(msg)
        self.assertEqual(t.messages[0], msg)

    def test_close(self):
        user = Customer("c1", "mail", "hash")
        t = SupportTicket("t1", user, "Help")
        t.close()
        self.assertEqual(t.status, "CLOSED")
