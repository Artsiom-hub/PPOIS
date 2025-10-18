from __future__ import annotations
from dataclasses import dataclass
from ..exceptions import AuthenticationError, AuthorizationError
from ..models.core import Credentials, PasswordHasher, User

@dataclass
class AuthService:
    hasher: PasswordHasher

    def authenticate(self, username:str, password:str, creds:Credentials) -> User:
        if not creds.check(self.hasher, password):
            raise AuthenticationError("bad password")
        return User(id=username, name=username, role="customer", creds=creds)

    def authorize(self, user:User, action:str) -> None:
        if not user.can(action):
            raise AuthorizationError(f"user {user.name} cannot {action}")
