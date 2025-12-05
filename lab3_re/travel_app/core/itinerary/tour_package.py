from dataclasses import dataclass, field
from typing import List

from core.flights.flights import Flight
from core.hotels.hotels import Hotel


@dataclass
class TourPackage:
    code: str
    name: str
    description: str
    flights: List[Flight] = field(default_factory=list)
    hotels: List[Hotel] = field(default_factory=list)
    base_price: float = 0.0

    def add_flight(self, flight: Flight) -> None:
        self.flights.append(flight)

    def add_hotel(self, hotel: Hotel) -> None:
        self.hotels.append(hotel)

    def calculate_price(self) -> float:
        """Полная цена пакета = базовая + сумма цен рейсов + коэффициент за отели."""
        flight_sum = sum(f.base_price for f in self.flights)
        hotel_factor = len(self.hotels) * 50.0
        return self.base_price + flight_sum + hotel_factor
