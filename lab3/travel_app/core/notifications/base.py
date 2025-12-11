from dataclasses import dataclass, field
import datetime

from core.users.models import User


@dataclass
class Notification:
    notification_id: str
    user: User
    message: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    read: bool = False

    def mark_read(self) -> None:
        self.read = True

    def short(self) -> str:
        """Короткое превью сообщения (первые 40 символов)."""
        return self.message[:40]
    def is_urgent(self) -> bool:
        """Определяет, является ли уведомление срочным по ключевым словам."""
        urgent_keywords = ["urgent", "immediate", "asap", "important", "alert"]
        message_lower = self.message.lower()
        return any(keyword in message_lower for keyword in urgent_keywords)