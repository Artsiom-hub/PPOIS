# lab2re/Unit_tests/test_CoreDomains/Test_User_Security.py

import pytest

from Core_Domains.User_Security.services import UserService
from Core_Domains.User_Security.auth_service import AuthService
from Core_Domains.User_Security.models import User, Role, Permission
from Core_Domains.User_Security.exceptions import (
    EmailAlreadyExists,
    InvalidCredentials,
    UserNotFound,
    UserBlocked
)
from Core_Domains.User_Security.value_objects import UserStatus
from Core_Domains.User_Security.password_hasher import PasswordHasher

from Core_Domains.User_Security.repository_interface import (
    UserRepository, RoleRepository
)


# ============================================================
#                 In-memory Repositories
# ============================================================

class InMemoryUserRepo(UserRepository):
    def __init__(self):
        self.users = {}
        self.by_email = {}

    def get(self, user_id: int) -> User:
        if user_id not in self.users:
            raise KeyError(user_id)
        return self.users[user_id]

    def get_by_email(self, email: str):
        return self.by_email.get(email)

    def save(self, user: User) -> None:
        self.users[user.id] = user
        self.by_email[user.email] = user


class InMemoryRoleRepo(RoleRepository):
    def __init__(self):
        self.roles = {}

    def get(self, role_id: int) -> Role:
        if role_id not in self.roles:
            raise KeyError(role_id)
        return self.roles[role_id]

    def list(self):
        return list(self.roles.values())

    def save(self, role: Role) -> None:
        self.roles[role.id] = role


# ============================================================
#                       Fixtures
# ============================================================

@pytest.fixture
def user_repo():
    return InMemoryUserRepo()

@pytest.fixture
def role_repo():
    return InMemoryRoleRepo()

@pytest.fixture
def service(user_repo, role_repo):
    return UserService(user_repo, role_repo)

@pytest.fixture
def auth(user_repo):
    return AuthService(user_repo)


# ============================================================
#                     TESTS — UserService
# ============================================================

def test_register_success(service, user_repo):
    user = service.register("alice@example.com", "password123")
    assert user.email == "alice@example.com"
    assert user_repo.get(user.id).email == "alice@example.com"


def test_register_email_exists(service, user_repo):
    service.register("bob@example.com", "pass1")

    with pytest.raises(EmailAlreadyExists):
        service.register("bob@example.com", "pass2")


def test_register_password_is_hashed(service, user_repo):
    user = service.register("john@example.com", "mypass")

    hasher = PasswordHasher()
    assert hasher.verify("mypass", user.password_hash)
    assert user.password_hash != "mypass"


def test_assign_role(service, role_repo, user_repo):
    # prepare role
    role = Role(id=1, name="admin")
    role_repo.save(role)

    # prepare user
    user = service.register("x@y.z", "123")

    service.assign_role(user.id, 1)

    saved = user_repo.get(user.id)
    assert saved.roles[0].name == "admin"


def test_assign_role_role_not_found(service, user_repo):
    user = service.register("user@site.com", "123")

    with pytest.raises(KeyError):
        service.assign_role(user.id, 999)


def test_assign_role_user_not_found(service):
    with pytest.raises(UserNotFound):
        service.assign_role(99999, 1)


def test_block_user(service, user_repo):
    user = service.register("test1@mail.com", "111")
    service.block_user(user.id)

    assert user_repo.get(user.id).status == UserStatus.BLOCKED


def test_unblock_user(service, user_repo):
    user = service.register("test2@mail.com", "111")
    service.block_user(user.id)

    service.unblock_user(user.id)
    assert user_repo.get(user.id).status == UserStatus.ACTIVE


def test_block_user_not_found(service):
    with pytest.raises(UserNotFound):
        service.block_user(99999)


# ============================================================
#                     TESTS — AuthService
# ============================================================

def test_authenticate_success(service, auth, user_repo):
    user = service.register("login@example.com", "secret")

    authenticated = auth.authenticate("login@example.com", "secret")
    assert authenticated.id == user.id


def test_authenticate_wrong_password(service, auth):
    service.register("u@mail.com", "correct")

    with pytest.raises(InvalidCredentials):
        auth.authenticate("u@mail.com", "wrong")


def test_authenticate_user_not_found(auth):
    with pytest.raises(InvalidCredentials):
        auth.authenticate("nouser@mail.com", "123456")


def test_authenticate_user_blocked(service, auth, user_repo):
    user = service.register("test@x.com", "123")
    service.block_user(user.id)

    with pytest.raises(UserBlocked):
        auth.authenticate("test@x.com", "123")


def test_permission_check(service, auth):
    # Create role with permission
    p = Permission(id=1, name="books.read")
    role = Role(id=1, name="reader", permissions=[p])

    # Manually create user
    hasher = PasswordHasher()
    user = User(
        id=1,
        email="x@y.com",
        password_hash=hasher.hash_password("111"),
        roles=[role]
    )

    assert auth.check_permission(user, "books.read") is True
    assert auth.check_permission(user, "orders.manage") is False
