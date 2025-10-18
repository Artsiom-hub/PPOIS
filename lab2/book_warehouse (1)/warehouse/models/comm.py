from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .core import User

@dataclass
class Notification:
    id: str
    user: User
    message: str
    read: bool = False

    def mark_read(self): self.read = True
    def preview(self) -> str: return self.message[:40]

@dataclass
class EmailService:
    sender: str
    sent: List[str] = field(default_factory=list)

    def send(self, to:str, subject:str, body:str):
        self.sent.append(f"TO:{to}|SUBJ:{subject}|{body}")

@dataclass
class SMSService:
    provider: str
    logs: List[str] = field(default_factory=list)

    def send(self, to:str, text:str):
        self.logs.append(f"SMS to {to}: {text}")
