import uuid
import hashlib
from typing import Dict

from core.users.session import Session
from core.users.models import User
from core.exceptions.travel_errors import InvalidPasswordError, AuthenticationError


class AuthenticationService:
    """Простая система аутентификации и управления сессиями."""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    @staticmethod
    def hash_password(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def authenticate(self, user: User, raw_password: str) -> Session:
        """Проверка пароля + создание новой сессии."""
        if not user.check_password(raw_password):
            raise InvalidPasswordError()

        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, user=user)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if not session or not session.is_active():
            raise AuthenticationError("Session expired or not found")
        return session
