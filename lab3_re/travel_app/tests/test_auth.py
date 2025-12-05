import unittest
from core.users.auth import AuthenticationService
from core.users.models import User
from core.exceptions.travel_errors import InvalidPasswordError


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.auth = AuthenticationService()
        hashed = self.auth.hash_password("secret")
        self.user = User("u1", "mail", hashed)

    def test_auth_success(self):
        session = self.auth.authenticate(self.user, "secret")
        self.assertTrue(session.is_active())

    def test_auth_fail(self):
        with self.assertRaises(InvalidPasswordError):
            self.auth.authenticate(self.user, "wrong")
