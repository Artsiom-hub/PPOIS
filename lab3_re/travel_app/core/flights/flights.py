from dataclasses import dataclass, field
import datetime
from typing import Dict

from core.exceptions.travel_errors import SeatUnavailableError
from core.geography.airports import Airport
from .seats import Seat


@dataclass
class Flight:
    flight_number: str
    origin: Airport
    destination: Airport
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    base_price: float
    seats: Dict[str, Seat] = field(default_factory=dict)

    def add_seat(self, seat: Seat) -> None:
        self.seats[seat.seat_number] = seat

    def reserve_seat(self, seat_number: str) -> Seat:
        seat = self.seats.get(seat_number)
        if not seat:
            raise SeatUnavailableError("Seat does not exist")
        seat.reserve()
        return seat

    def available_seats_count(self) -> int:
        return sum(1 for s in self.seats.values() if not s.is_occupied)
