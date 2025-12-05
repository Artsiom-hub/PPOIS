from __future__ import annotations
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.users.models import Customer


class Booking:
    def __init__(
        self,
        booking_id: str,
        customer: "Customer",
        created_at: datetime.datetime,
        total_price: float
    ):
        self.booking_id = booking_id
        self.customer = customer
        self.created_at = created_at
        self.total_price = total_price
        self.status = "PENDING"

    def confirm(self):
        self.status = "CONFIRMED"

    def cancel(self):
        self.status = "CANCELLED"
