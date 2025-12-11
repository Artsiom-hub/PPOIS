class UserSecurityError(Exception):
    pass


class UserNotFound(UserSecurityError):
    def __init__(self, user_id):
        super().__init__(f"User {user_id} not found")


class EmailAlreadyExists(UserSecurityError):
    def __init__(self, email):
        super().__init__(f"Email already registered: {email}")


class InvalidCredentials(UserSecurityError):
    def __init__(self):
        super().__init__("Invalid email or password")


class UserBlocked(UserSecurityError):
    def __init__(self):
        super().__init__("User account is blocked")


# === ДОБАВЬ ЭТИ ДВА ИСКЛЮЧЕНИЯ ===

class WrongPassword(UserSecurityError):
    def __init__(self, user_id: int):
        super().__init__(f"Wrong password for user {user_id}")
        self.user_id = user_id


class UserBlocked(UserSecurityError):
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} is blocked")
        self.user_id = user_id
