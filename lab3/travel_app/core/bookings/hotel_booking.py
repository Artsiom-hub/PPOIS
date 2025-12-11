from __future__ import annotations
import datetime
from typing import TYPE_CHECKING

from core.bookings.base import Booking

if TYPE_CHECKING:
    from core.users.models import Customer
    from core.hotels.hotels import Hotel
    from core.hotels.rooms import Room


class HotelBooking(Booking):
    def __init__(
        self,
        booking_id: str,
        customer: "Customer",
        created_at: datetime.datetime,
        total_price: float,
        hotel: "Hotel",
        room: "Room",
        check_in: datetime.date,
        check_out: datetime.date
    ):
        super().__init__(booking_id, customer, created_at, total_price)
        self.hotel = hotel
        self.room = room
        self.check_in = check_in
        self.check_out = check_out

    def nights(self) -> int:
        return (self.check_out - self.check_in).days
