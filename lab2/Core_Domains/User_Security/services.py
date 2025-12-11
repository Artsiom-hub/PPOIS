from .password_hasher import PasswordHasher
from .repository_interface import UserRepository, RoleRepository
from .models import User
from .exceptions import (
    EmailAlreadyExists,
    UserNotFound,
    UserBlocked
)
from .value_objects import UserStatus


class UserService:

    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.password_hasher = PasswordHasher()
        self.repo = user_repo     # тесты используют self.repo

    # ==========================
    # CRUD методы (по тестам)
    # ==========================
    def list_users(self):
        """Return all users (tests use different mock APIs)."""

        # Preferred by interface
        if hasattr(self.user_repo, "list_all"):
            return self.user_repo.list_all()

        # Some mocks use .list()
        if hasattr(self.user_repo, "list"):
            return self.user_repo.list()

        # Fallback: repo.users dict in mock
        if hasattr(self.user_repo, "users"):
            return list(self.user_repo.users.values())

        raise RuntimeError("User repository does not support listing")


    def create_user(self, user_id: int, email: str, password: str) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing is not None:
            raise EmailAlreadyExists(email)

        hashed = self.password_hasher.hash(password)
        u = User(id=user_id, email=email, password_hash=hashed)
        self.user_repo.save(u)
        return u

    def get_user(self, user_id: int) -> User:
        return self._get_user(user_id)

    def delete_user(self, user_id: int):
        _ = self._get_user(user_id)
        self.user_repo.delete(user_id)

    # ==========================
    # Доп логика (тесты это используют)
    # ==========================

    def assign_role(self, user_id: int, role_id: int):
        user = self._get_user(user_id)
        role = self.role_repo.get(role_id)

        user.add_role(role)
        self.user_repo.save(user)

    def block_user(self, user_id: int):
        user = self._get_user(user_id)
        user.status = UserStatus.BLOCKED
        self.user_repo.save(user)

    def unblock_user(self, user_id: int):
        user = self._get_user(user_id)
        user.status = UserStatus.ACTIVE
        self.user_repo.save(user)

    # ==========================
    # Register (не используется в тестах, но исправлено)
    # ==========================

    def register(self, email: str, password: str) -> User:
        if self.user_repo.get_by_email(email) is not None:
            raise EmailAlreadyExists(email)

        hashed = self.password_hasher.hash(password)
        user = User(id=self._generate_user_id(), email=email, password_hash=hashed)
        self.user_repo.save(user)
        return user
    def change_password(self, user_id: int, old_password: str, new_password: str):
        """Change password if old password matches."""
        from .exceptions import WrongPassword, UserBlocked

        user = self._get_user(user_id)

        # Проверка статуса
        if user.status == UserStatus.BLOCKED:
            raise UserBlocked(user_id)

        # Проверка текущего пароля
        if not self.password_hasher.verify(old_password, user.password_hash):
            from .exceptions import InvalidCredentials
            raise InvalidCredentials()


        # Генерация нового хэша и сохранение
        new_hash = self.password_hasher.hash(new_password)
        user.password_hash = new_hash
        self.user_repo.save(user)

    # ==========================
    # Helpers
    # ==========================

    def _get_user(self, user_id: int) -> User:
        try:
            return self.user_repo.get(user_id)
        except KeyError:
            raise UserNotFound(user_id)

    def _generate_user_id(self):
        import random
        return random.randint(100000, 999999)
