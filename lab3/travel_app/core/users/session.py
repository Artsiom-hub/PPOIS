from dataclasses import dataclass, field
import datetime

from core.users.models import User


@dataclass
class Session:
    session_id: str
    user: User
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    expires_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    )

    def is_active(self) -> bool:
        return datetime.datetime.utcnow() < self.expires_at

    def extend(self, hours: int = 1) -> None:
        self.expires_at += datetime.timedelta(hours=hours)
