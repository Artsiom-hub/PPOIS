from dataclasses import dataclass
from typing import List


@dataclass
class RoomType:
    name: str              # e.g. "Standard", "Deluxe"
    capacity: int          # number of guests
    amenities: List[str]   # list of amenities

    def add_amenity(self, amenity: str) -> None:
        if amenity not in self.amenities:
            self.amenities.append(amenity)


@dataclass
class Room:
    room_number: str
    room_type: RoomType
    price_per_night: float
    is_available: bool = True

    def reserve(self) -> None:
        self.is_available = False

    def release(self) -> None:
        self.is_available = True
