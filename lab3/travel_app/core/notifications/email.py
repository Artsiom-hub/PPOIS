from dataclasses import dataclass

from core.notifications.base import Notification


@dataclass
class EmailNotification(Notification):
    subject: str = ""
    email_address: str = ""

    def format_email(self) -> str:
        """Готовит полноформатное письмо для отправки."""
        return (
            f"To: {self.email_address}\n"
            f"Subject: {self.subject}\n\n"
            f"{self.message}"
        )
    def is_promotional(self) -> bool:
        """Определяет, является ли письмо рекламным по ключевым словам."""
        promo_keywords = ["sale", "discount", "offer", "promotion", "deal"]
        message_lower = self.message.lower()
        return any(keyword in message_lower for keyword in promo_keywords)