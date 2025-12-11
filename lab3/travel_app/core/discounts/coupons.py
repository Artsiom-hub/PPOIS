from dataclasses import dataclass
import datetime

from core.exceptions.travel_errors import CouponExpiredError


@dataclass
class Coupon:
    code: str
    discount_percent: float
    expires_at: datetime.datetime
    used: bool = False

    def apply(self, total: float) -> float:
        # Проверка истечения срока или повторного использования
        if self.used or datetime.datetime.utcnow() > self.expires_at:
            raise CouponExpiredError("Coupon cannot be used")

        self.used = True
        return total * (1 - self.discount_percent / 100.0)
