class TravelError(Exception):
    """Base exception for travel system."""

    def __init__(self, message: str, code: str = "TRAVEL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
