import unittest

from core.notifications.base import Notification
from core.notifications.email import EmailNotification
from core.notifications.sms import SMSNotification
from core.users.models import User


class TestNotification(unittest.TestCase):
    def setUp(self):
        self.user = User("u1", "mail", "hash")
        self.n = Notification("n1", self.user, "Hello World")

    def test_mark_read(self):
        self.n.mark_read()
        self.assertTrue(self.n.read)

    def test_short(self):
        self.assertEqual(self.n.short(), "Hello World")


class TestEmailNotification(unittest.TestCase):
    def test_format_email(self):
        user = User("u1", "mail", "hash")
        mail = EmailNotification(
            "n1", user, "Body",
            subject="Subj",
            email_address="user@mail.com"
        )
        body = mail.format_email()
        self.assertIn("To: user@mail.com", body)
        self.assertIn("Subject: Subj", body)
        self.assertIn("Body", body)


class TestSMSNotification(unittest.TestCase):
    def test_format_sms(self):
        user = User("u1", "mail", "hash")
        sms = SMSNotification("n1", user, "Hi", phone_number="123")
        msg = sms.format_sms()
        self.assertEqual(msg, "SMS to 123: Hi")
