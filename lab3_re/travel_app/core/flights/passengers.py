from dataclasses import dataclass, field
from typing import List
import datetime

from core.users.models import Customer


@dataclass
class Baggage:
    tag: str
    weight_kg: float
    is_cabin: bool = False

    def overweight_fee(self, limit: float, fee_per_kg: float) -> float:
        if self.weight_kg <= limit:
            return 0.0
        return (self.weight_kg - limit) * fee_per_kg


@dataclass
class PassengerProfile:
    customer: Customer
    passport_number: str
    nationality: str
    date_of_birth: datetime.date
    baggage: List[Baggage] = field(default_factory=list)

    def add_baggage(self, bag: Baggage) -> None:
        self.baggage.append(bag)

    def age(self) -> int:
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
