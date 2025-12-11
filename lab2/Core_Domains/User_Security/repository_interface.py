from abc import ABC, abstractmethod
from typing import Optional, List
from .models import User, Role, Permission


class UserRepository(ABC):

    @abstractmethod
    def get(self, user_id: int) -> User:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass


class RoleRepository(ABC):

    @abstractmethod
    def get(self, role_id: int) -> Role:
        pass

    @abstractmethod
    def list(self) -> List[Role]:
        pass

    @abstractmethod
    def save(self, role: Role) -> None:
        pass


class PermissionRepository(ABC):

    @abstractmethod
    def get(self, perm_id: int) -> Permission:
        pass

    @abstractmethod
    def list(self) -> List[Permission]:
        pass

    @abstractmethod
    def save(self, perm: Permission) -> None:
        pass
