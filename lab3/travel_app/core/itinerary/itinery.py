from dataclasses import dataclass, field
from typing import List

from core.users.models import Customer
from core.bookings.flight_booking import FlightBooking
from core.bookings.hotel_booking import HotelBooking


@dataclass
class Itinerary:
    code: str
    customer: Customer
    flight_bookings: List[FlightBooking] = field(default_factory=list)
    hotel_bookings: List[HotelBooking] = field(default_factory=list)

    def add_flight_booking(self, fb: FlightBooking) -> None:
        self.flight_bookings.append(fb)

    def add_hotel_booking(self, hb: HotelBooking) -> None:
        self.hotel_bookings.append(hb)

    def total_cost(self) -> float:
        return sum(
            b.total_price
            for b in (self.flight_bookings + self.hotel_bookings)
        )
    def booking_count(self) -> int:
        return len(self.flight_bookings) + len(self.hotel_bookings)