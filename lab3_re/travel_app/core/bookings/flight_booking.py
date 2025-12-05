from __future__ import annotations
import datetime
from typing import Optional, TYPE_CHECKING

from core.bookings.base import Booking

if TYPE_CHECKING:
    from core.users.models import Customer
    from core.flights.flights import Flight
    from core.flights.passengers import PassengerProfile, Baggage
    from core.flights.seats import Seat


class FlightBooking(Booking):
    def __init__(
        self,
        booking_id: str,
        customer: "Customer",
        created_at: datetime.datetime,
        total_price: float,
        flight: "Flight",
        passenger: "PassengerProfile"
    ):
        super().__init__(booking_id, customer, created_at, total_price)
        self.flight = flight
        self.passenger = passenger
        self.seat: Optional["Seat"] = None
        self.baggage_fees = 0

    def assign_seat(self, seat: "Seat"):
        self.seat = seat

    def add_baggage_fee(self, amount: float):
        self.baggage_fees += amount
        self.total_price += amount
