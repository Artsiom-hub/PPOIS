from dataclasses import dataclass, field
from typing import List
from .value_objects import UserStatus


@dataclass
class Permission:
    id: int
    name: str  # e.g. "books.read", "orders.manage"


@dataclass
class Role:
    id: int
    name: str  # e.g. "admin", "manager", "customer"
    permissions: List[Permission] = field(default_factory=list)

    def add_permission(self, perm: Permission):
        if perm not in self.permissions:
            self.permissions.append(perm)


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    roles: List[Role] = field(default_factory=list)
    status: UserStatus = UserStatus.ACTIVE

    def add_role(self, role: Role):
        if role not in self.roles:
            self.roles.append(role)

    def has_permission(self, permission_name: str) -> bool:
        for role in self.roles:
            for perm in role.permissions:
                if perm.name == permission_name:
                    return True
        return False
