import pytest

from Core_Domains.User_Security.services import UserService      # :contentReference[oaicite:2]{index=2}
from Core_Domains.User_Security.auth_service import AuthService  # :contentReference[oaicite:3]{index=3}
from Core_Domains.User_Security.password_hasher import PasswordHasher
from Core_Domains.User_Security.models import User
from Core_Domains.User_Security.exceptions import (
    UserNotFound,
    EmailAlreadyExists,
    InvalidCredentials,
    UserBlocked
)                                                                # :contentReference[oaicite:4]{index=4}


# ============================
# Mock Repos
# ============================

class UserRepoMock:
    def __init__(self):
        self.data = {}

    def save(self, u):
        self.data[u.id] = u

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def delete(self, id):
        self.data.pop(id, None)

    def get_by_email(self, email):
        for u in self.data.values():
            if u.email == email:
                return u
        return None

    def list(self):
        return list(self.data.values())


class RoleRepoMock:
    def __init__(self):
        pass  # твой сервис фактически роли НЕ использует


# ============================
# Fixtures
# ============================

@pytest.fixture
def service():
    return UserService(UserRepoMock(), RoleRepoMock())

@pytest.fixture
def auth():
    return AuthService(UserRepoMock())


# ============================
# UserService Tests
# ============================

def test_create_user(service):
    u = service.create_user(1, "a@mail.com", "pass")
    assert u.id == 1


def test_create_user_duplicate(service):
    service.create_user(1, "a@mail.com", "pass")
    with pytest.raises(EmailAlreadyExists):
        service.create_user(2, "a@mail.com", "xxx")


def test_get_user(service):
    service.create_user(1, "a@mail.com", "pass")
    u = service.get_user(1)
    assert u.id == 1


def test_get_user_not_found(service):
    with pytest.raises(UserNotFound):
        service.get_user(999)


def test_delete_user(service):
    service.create_user(1, "a@mail.com", "pass")
    service.delete_user(1)
    with pytest.raises(UserNotFound):
        service.get_user(1)


def test_change_password_ok(service):
    service.create_user(1, "a@mail.com", "old")
    service.change_password(1, "old", "new")
    u = service.get_user(1)
    assert PasswordHasher.verify("new", u.password_hash)


def test_change_password_wrong_old(service):
    service.create_user(1, "a@mail.com", "old")
    with pytest.raises(InvalidCredentials):
        service.change_password(1, "WRONG", "new")


def test_list_users(service):
    service.create_user(1, "a@mail.com", "pass")
    service.create_user(2, "b@mail.com", "pass")
    assert len(service.list_users()) == 2


# ============================
# AuthService Tests
# ============================

def test_auth_login_ok(auth):
    hashed = PasswordHasher.hash("pass")
    auth.user_repo.save(User(id=1, email="a@mail.com", password_hash=hashed))

    token = auth.login("a@mail.com", "pass")
    assert isinstance(token, str)


def test_auth_login_wrong_password(auth):
    hashed = PasswordHasher.hash("pass")
    auth.user_repo.save(User(id=1, email="a@mail.com", password_hash=hashed))

    with pytest.raises(InvalidCredentials):
        auth.login("a@mail.com", "WRONG")


def test_auth_login_user_not_found(auth):
    with pytest.raises(InvalidCredentials):
        auth.login("none@mail.com", "pass")


def test_auth_register(auth):
    u = auth.register(1, "a@mail.com", "pass")
    assert PasswordHasher.verify("pass", u.password_hash)


def test_auth_register_duplicate(auth):
    auth.register(1, "a@mail.com", "pass")
    with pytest.raises(EmailAlreadyExists):
        auth.register(2, "a@mail.com", "xxx")


def test_password_hasher():
    h = PasswordHasher.hash("hello")
    assert PasswordHasher.verify("hello", h)
    assert not PasswordHasher.verify("bad", h)
