from .base import TravelError


class InvalidPasswordError(TravelError):
    def __init__(self, message: str = "Invalid password"):
        super().__init__(message, code="INVALID_PASSWORD")


class AuthenticationError(TravelError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTH_FAILED")


class PaymentDeclinedError(TravelError):
    def __init__(self, message: str = "Payment declined"):
        super().__init__(message, code="PAYMENT_DECLINED")


class InsufficientFundsError(TravelError):
    def __init__(self, message: str = "Insufficient funds"):
        super().__init__(message, code="INSUFFICIENT_FUNDS")


class CardNotFoundError(TravelError):
    def __init__(self, message: str = "Card not found"):
        super().__init__(message, code="CARD_NOT_FOUND")


class BookingNotFoundError(TravelError):
    def __init__(self, message: str = "Booking not found"):
        super().__init__(message, code="BOOKING_NOT_FOUND")


class SeatUnavailableError(TravelError):
    def __init__(self, message: str = "Seat is not available"):
        super().__init__(message, code="SEAT_UNAVAILABLE")


class OverbookingError(TravelError):
    def __init__(self, message: str = "Too many passengers for this resource"):
        super().__init__(message, code="OVERBOOKING")


class CouponExpiredError(TravelError):
    def __init__(self, message: str = "Coupon has expired"):
        super().__init__(message, code="COUPON_EXPIRED")


class InvalidSearchCriteriaError(TravelError):
    def __init__(self, message: str = "Invalid search criteria"):
        super().__init__(message, code="INVALID_SEARCH_CRITERIA")


class UnauthorizedActionError(TravelError):
    def __init__(self, message: str = "You are not allowed to perform this action"):
        super().__init__(message, code="UNAUTHORIZED")
