import smtplib
from email.mime.text import MIMEText
from Infrastructure.Config.settings import get_settings


class SmtpEmailService:
    def __init__(self):
        settings = get_settings()
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.login = settings.SMTP_LOGIN
        self.password = settings.SMTP_PASSWORD

    def send_email(self, to: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.login
        msg["To"] = to

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.login, self.password)
            server.send_message(msg)
