from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.geography.locations import City


class Airport:
    def __init__(self, code: str, name: str, city: "City"):
        self.code = code
        self.name = name
        self.city = city
        self.terminals: List[str] = []

    def add_terminal(self, terminal: str):
        self.terminals.append(terminal)

    def full_description(self):
        return f"{self.name} ({self.code}), {self.city.name}, {self.city.country.code}"
