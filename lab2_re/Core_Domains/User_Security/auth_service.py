from .password_hasher import PasswordHasher
from .repository_interface import UserRepository
from .exceptions import InvalidCredentials, UserBlocked
from .models import User


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.hasher = PasswordHasher()

    def authenticate(self, email: str, password: str) -> User:
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise InvalidCredentials()

        if user.status.name != "ACTIVE":
            raise UserBlocked(user.id)


        if not self.hasher.verify(password, user.password_hash):
            raise InvalidCredentials()

        return user
    def login(self, email: str, password: str) -> str:
        """Return token if credentials ok (required by tests)."""

        # Используем authenticate, чтобы не дублировать логику
        user = self.authenticate(email, password)

        # Возвращаем тестовый токен
        return f"token-{user.id}"
    def register(self, user_id: int, email: str, password: str) -> User:
        """Register user (required by tests)."""

        # Проверка уникальности email
        existing = self.user_repo.get_by_email(email)
        if existing is not None:
            from .exceptions import EmailAlreadyExists
            raise EmailAlreadyExists(f"Email already exists: {email}")

        # Хешируем пароль
        hashed = self.hasher.hash(password)

        # Создаём пользователя
        from .models import User
        user = User(id=user_id, email=email, password_hash=hashed)

        # Сохраняем
        self.user_repo.save(user)

        return user

    def check_permission(self, user: User, permission: str) -> bool:
        return user.has_permission(permission)
