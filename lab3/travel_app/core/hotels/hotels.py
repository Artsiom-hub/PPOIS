from dataclasses import dataclass, field
from typing import List, Optional

from .rooms import Room, RoomType
from core.geography.locations import City


@dataclass
class Hotel:
    name: str
    city: City
    rooms: List[Room] = field(default_factory=list)
    rating: float = 0.0

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def find_available_room(self, room_type: RoomType) -> Optional[Room]:
        for room in self.rooms:
            if room.room_type == room_type and room.is_available:
                return room
        return None

    def available_rooms_count(self) -> int:
        return sum(1 for r in self.rooms if r.is_available)
    def average_room_price(self) -> float:
        if not self.rooms:
            return 0.0
        total_price = sum(room.price_per_night for room in self.rooms)
        return total_price / len(self.rooms)