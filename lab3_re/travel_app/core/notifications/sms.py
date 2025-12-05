from dataclasses import dataclass

from core.notifications.base import Notification


@dataclass
class SMSNotification(Notification):
    phone_number: str = ""

    def format_sms(self) -> str:
        """Готовит форматированное SMS-сообщение."""
        return f"SMS to {self.phone_number}: {self.message}"
    def is_promotional(self) -> bool:
        """Определяет, является ли SMS рекламным по ключевым словам."""
        promo_keywords = ["sale", "discount", "offer", "promotion", "deal"]
        message_lower = self.message.lower()
        return any(keyword in message_lower for keyword in promo_keywords)