# Core_Domains/User_Security/password_hasher.py
import hashlib
import os
import base64


class PasswordHasher:
    SALT_LENGTH = 16
    ITERATIONS = 100_000
    ALGORITHM = "sha256"

    @staticmethod
    def hash(password: str) -> str:
        """Create salted SHA256 hash."""
        salt = os.urandom(16).hex()
        digest = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${digest}"

    @staticmethod
    def verify(password: str, stored_hash: str) -> bool:
        """Validate password against stored salted hash."""
        try:
            salt, digest = stored_hash.split("$", 1)
        except ValueError:
            return False

        new_digest = hashlib.sha256((salt + password).encode()).hexdigest()
        return new_digest == digest

    def hash_password(self, raw_password: str) -> str:
        salt = os.urandom(self.SALT_LENGTH)
        hash_bytes = hashlib.pbkdf2_hmac(
            self.ALGORITHM,
            raw_password.encode(),
            salt,
            self.ITERATIONS
        )
        return base64.b64encode(salt + hash_bytes).decode()
