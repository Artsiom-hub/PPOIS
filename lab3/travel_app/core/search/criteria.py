from dataclasses import dataclass
from typing import Optional
import datetime

from core.geography.airports import Airport
from core.exceptions.travel_errors import InvalidSearchCriteriaError


@dataclass
class SearchCriteria:
    origin: Optional[Airport] = None
    destination: Optional[Airport] = None
    departure_date: Optional[datetime.date] = None
    max_price: Optional[float] = None

    def validate(self) -> None:
        if not self.origin or not self.destination:
            raise InvalidSearchCriteriaError("Origin and destination required")

        if self.origin == self.destination:
            raise InvalidSearchCriteriaError("Origin and destination must differ")
