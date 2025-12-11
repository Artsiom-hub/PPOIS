from dataclasses import dataclass


@dataclass
class Discount:
    name: str
    percent: float
    min_amount: float

    def apply_if_applicable(self, total: float) -> float:
        if total >= self.min_amount:
            return total * (1 - self.percent / 100.0)
        return total
