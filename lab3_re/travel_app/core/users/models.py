from __future__ import annotations
import hashlib
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.payments.models import PaymentCard
    from core.loyalty.account import LoyaltyAccount
    from core.bookings.base import Booking


class User:
    def __init__(self, user_id: str, email: str, password_hash: str):
        self.user_id = user_id
        self.email = email
        self.password_hash = password_hash
        self.active = True

    def check_password(self, raw: str) -> bool:
        return hashlib.sha256(raw.encode()).hexdigest() == self.password_hash

    def deactivate(self):
        self.active = False


class Customer(User):
    def __init__(self, user_id: str, email: str, password_hash: str, full_name: str = ""):
        super().__init__(user_id, email, password_hash)
        self.full_name = full_name or email
        self.cards: List["PaymentCard"] = []
        self.loyalty_account: Optional["LoyaltyAccount"] = None

    def add_card(self, card: "PaymentCard"):
        self.cards.append(card)

    def get_default_card(self) -> "PaymentCard":
        if not self.cards:
            from core.exceptions.travel_errors import CardNotFoundError
            raise CardNotFoundError("No payment cards found")
        return self.cards[0]


class TravelAgent(User):
    def __init__(
        self,
        user_id: str,
        email: str,
        password_hash: str,
        agency_name: str,
        commission_rate: float
    ):
        super().__init__(user_id, email, password_hash)
        self.agency_name = agency_name
        self.commission_rate = commission_rate
        self.managed_bookings: List["Booking"] = []

    def register_booking(self, booking: "Booking"):
        self.managed_bookings.append(booking)

    def calculate_commission(self, booking: "Booking"):
        return booking.total_price * self.commission_rate
