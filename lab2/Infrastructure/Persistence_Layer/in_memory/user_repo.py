# Infrastructure/persistence/in_memory/user_repo.py

from Core_Domains.User_Security.repository_interface import (
    UserRepository, RoleRepository, PermissionRepository
)


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users = {}
        self.users_by_email = {}

    def get(self, user_id: int):
        return self.users[user_id]

    def get_by_email(self, email: str):
        return self.users_by_email.get(email)

    def save(self, user):
        self.users[user.id] = user
        self.users_by_email[user.email] = user


class InMemoryRoleRepository(RoleRepository):
    def __init__(self):
        self.data = {}

    def get(self, role_id: int):
        return self.data[role_id]

    def list(self):
        return list(self.data.values())

    def save(self, role):
        self.data[role.id] = role


class InMemoryPermissionRepository(PermissionRepository):
    def __init__(self):
        self.data = {}

    def get(self, perm_id: int):
        return self.data[perm_id]

    def list(self):
        return list(self.data.values())

    def save(self, perm):
        self.data[perm.id] = perm
