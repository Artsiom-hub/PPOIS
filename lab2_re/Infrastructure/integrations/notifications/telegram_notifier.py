import requests
from Infrastructure.Config.settings import get_settings


class TelegramNotifier:

    def __init__(self):
        settings = get_settings()
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    def send(self, message: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message}
        requests.post(url, data=data)
