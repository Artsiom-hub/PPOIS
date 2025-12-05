import pytest

from Core_Domains.User_Security.services import UserService
from Core_Domains.User_Security.auth_service import AuthService
from Core_Domains.User_Security.password_hasher import PasswordHasher
from Core_Domains.User_Security.models import User
from Core_Domains.User_Security.exceptions import (
    UserNotFound,
    EmailAlreadyExists,
    InvalidCredentials,
)  # ← ЭТО правильные исключения!

# ================================
# Mock repos
# ================================

class UserRepoMock:
    def __init__(self):
        self.data = {}

    def save(self, user):
        self.data[user.id] = user

    def get(self, user_id):
        if user_id not in self.data:
            raise KeyError
        return self.data[user_id]

    def delete(self, user_id):
        self.data.pop(user_id, None)

    def get_by_email(self, email):
        for u in self.data.values():
            if u.email == email:
                return u
        return None

    def list(self):
        return list(self.data.values())


class RoleRepoMock:
    pass  # твой сервис не использует роли


# ================================
# Fixtures
# ================================

@pytest.fixture
def user_service():
    return UserService(UserRepoMock(), RoleRepoMock())


@pytest.fixture
def auth_service():
    return AuthService(UserRepoMock())


# ================================
# Tests
# ================================

def test_create_user(user_service):
    u = user_service.create_user(1, "a@mail.com", "pass")
    assert u.id == 1


def test_create_user_duplicate(user_service):
    user_service.create_user(1, "a@mail.com", "123")
    with pytest.raises(EmailAlreadyExists):
        user_service.create_user(2, "a@mail.com", "xxx")


def test_get_user(user_service):
    user_service.create_user(1, "a@mail.com", "pass")
    u = user_service.get_user(1)
    assert u.id == 1


def test_get_user_not_found(user_service):
    with pytest.raises(UserNotFound):
        user_service.get_user(999)


def test_change_password_ok(user_service):
    user_service.create_user(1, "a@mail.com", "oldpass")
    user_service.change_password(1, "oldpass", "newpass")
    u = user_service.get_user(1)
    assert PasswordHasher.verify("newpass", u.password_hash)


def test_change_password_wrong(user_service):
    user_service.create_user(1, "a@mail.com", "oldpass")
    with pytest.raises(InvalidCredentials):
        user_service.change_password(1, "wrong", "newpass")


def test_delete_user(user_service):
    user_service.create_user(1, "a@mail.com", "pass")
    user_service.delete_user(1)
    with pytest.raises(UserNotFound):
        user_service.get_user(1)


def test_list_users(user_service):
    user_service.create_user(1, "a@mail.com", "pass")
    user_service.create_user(2, "b@mail.com", "pass")
    lst = user_service.list_users()
    assert len(lst) == 2


# ================================
# AuthService
# ================================

def test_auth_login(auth_service):
    hashed = PasswordHasher.hash("pass")
    auth_service.user_repo.save(User(id=1, email="a@mail.com", password_hash=hashed))

    token = auth_service.login("a@mail.com", "pass")
    assert isinstance(token, str)
    assert len(token) > 5


def test_auth_login_wrong(auth_service):
    hashed = PasswordHasher.hash("pass")
    auth_service.user_repo.save(User(id=1, email="a@mail.com", password_hash=hashed))

    with pytest.raises(InvalidCredentials):
        auth_service.login("a@mail.com", "WRONG")


def test_auth_login_unknown(auth_service):
    with pytest.raises(InvalidCredentials):
        auth_service.login("none@mail.com", "pass")


def test_auth_register(auth_service):
    u = auth_service.register(1, "a@mail.com", "pass")
    assert PasswordHasher.verify("pass", u.password_hash)


def test_auth_register_duplicate(auth_service):
    auth_service.register(1, "a@mail.com", "pass")
    with pytest.raises(EmailAlreadyExists):
        auth_service.register(2, "a@mail.com", "pass2")
