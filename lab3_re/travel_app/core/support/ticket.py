from dataclasses import dataclass, field
from typing import List

from core.users.models import Customer
from core.support.message import ChatMessage


@dataclass
class SupportTicket:
    ticket_id: str
    customer: Customer
    subject: str
    messages: List[ChatMessage] = field(default_factory=list)
    status: str = "OPEN"   # OPEN, CLOSED

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def close(self) -> None:
        self.status = "CLOSED"
    def message_count(self) -> int:
        return len(self.messages)