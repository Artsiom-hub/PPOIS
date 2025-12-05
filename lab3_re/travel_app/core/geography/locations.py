from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.geography.airports import Airport


class Country:
    def __init__(self, code: str, name: str, currency: str):
        self.code = code
        self.name = name
        self.currency = currency
        self.airports: List["Airport"] = []

    def add_airport(self, airport: "Airport"):
        self.airports.append(airport)

    def find_airport(self, code: str) -> "Airport | None":
        for a in self.airports:
            if a.code == code:
                return a
        return None


class City:
    def __init__(self, name: str, country: Country, population: int = 0):
        self.name = name
        self.country = country
        self.population = population

    def describe(self):
        return f"{self.name}, {self.country.name}. Population: {self.population}"
