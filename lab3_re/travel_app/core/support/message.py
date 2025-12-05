from dataclasses import dataclass, field
import datetime

from core.users.models import User


@dataclass
class ChatMessage:
    message_id: str
    author: User
    text: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def preview(self) -> str:
        """Возвращает первые 44 символа сообщения."""
        return self.text[:44]
    def is_long_message(self) -> bool:
        """Определяет, является ли сообщение длинным (более 200 символов)."""
        return len(self.text) > 200 