from dataclasses import dataclass

from core.exceptions.travel_errors import SeatUnavailableError


@dataclass
class Seat:
    seat_number: str
    seat_class: str  # Economy, Business
    is_window: bool
    is_occupied: bool = False

    def reserve(self) -> None:
        if self.is_occupied:
            raise SeatUnavailableError(f"Seat {self.seat_number} already occupied")
        self.is_occupied = True

    def free(self) -> None:
        self.is_occupied = False
