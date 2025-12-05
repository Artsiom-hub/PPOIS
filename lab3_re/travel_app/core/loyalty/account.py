from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.bookings.base import Booking
    from core.users.models import Customer
    from core.loyalty.program import LoyaltyProgram


class LoyaltyAccount:
    def __init__(self, customer: "Customer", program: "LoyaltyProgram"):
        self.customer = customer
        self.program = program
        self.points = 0
        self.level = "NONE"

    def add_points_for_booking(self, booking: "Booking"):
        earned = int(booking.total_price * self.program.base_multiplier)
        self.points += earned
        self.level = self.program.level_for_points(self.points)

    def redeem_points(self, amount: int):
        if amount > self.points:
            raise Exception("Not enough loyalty points")
        self.points -= amount
