from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid
import datetime
import hashlib


# ===========================
#      CUSTOM EXCEPTIONS
# ===========================

class TravelError(Exception):
    """Base exception for travel system."""

    def __init__(self, message: str, code: str = "TRAVEL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


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


# ===========================
#        CORE ENTITIES
# ===========================

@dataclass
class User:
    user_id: str
    email: str
    password_hash: str
    active: bool = True
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def check_password(self, raw_password: str) -> bool:
        """Проверка, что пароль верный."""
        hashed = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
        return hashed == self.password_hash

    def deactivate(self) -> None:
        self.active = False


@dataclass
class Customer(User):
    full_name: str = ""
    loyalty_account: Optional["LoyaltyAccount"] = None
    cards: List["PaymentCard"] = field(default_factory=list)

    def add_card(self, card: "PaymentCard") -> None:
        self.cards.append(card)

    def get_default_card(self) -> "PaymentCard":
        if not self.cards:
            raise CardNotFoundError("Customer has no payment cards")
        return self.cards[0]


@dataclass
class TravelAgent(User):
    agency_name: str = ""
    commission_rate: float = 0.05
    managed_bookings: List["Booking"] = field(default_factory=list)

    def register_booking(self, booking: "Booking") -> None:
        self.managed_bookings.append(booking)

    def calculate_commission(self, booking: "Booking") -> float:
        return booking.total_price * self.commission_rate


@dataclass
class BankAccount:
    iban: str
    owner_name: str
    balance: float = 0.0
    currency: str = "EUR"

    def deposit(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Negative deposit")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientFundsError("Not enough money on bank account")
        self.balance -= amount


@dataclass
class PaymentCard:
    card_number: str
    owner: Customer
    bank_account: BankAccount
    cvv: str
    expiry_month: int
    expiry_year: int
    label: str = "Main card"

    def is_valid(self, now: Optional[datetime.date] = None) -> bool:
        now = now or datetime.date.today()
        return (self.expiry_year, self.expiry_month) >= (now.year, now.month)

    def charge(self, amount: float) -> None:
        if not self.is_valid():
            raise PaymentDeclinedError("Card expired")
        self.bank_account.withdraw(amount)

    def refund(self, amount: float) -> None:
        self.bank_account.deposit(amount)


@dataclass
class Transaction:
    tx_id: str
    from_card: PaymentCard
    to_card: PaymentCard
    amount: float
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    status: str = "PENDING"  # PENDING, SUCCESS, FAILED
    failure_reason: Optional[str] = None

    def mark_success(self) -> None:
        self.status = "SUCCESS"
        self.failure_reason = None

    def mark_failed(self, reason: str) -> None:
        self.status = "FAILED"
        self.failure_reason = reason


class PaymentGateway:
    """Очень упрощённый шлюз платежей."""

    def __init__(self, name: str):
        self.name = name
        self.transactions: Dict[str, Transaction] = {}

    def transfer(self, from_card: PaymentCard, to_card: PaymentCard, amount: float) -> Transaction:
        """Перевод денег с одной карты на другую."""
        tx_id = str(uuid.uuid4())
        tx = Transaction(tx_id=tx_id, from_card=from_card, to_card=to_card, amount=amount)
        self.transactions[tx_id] = tx

        try:
            from_card.charge(amount)
            to_card.refund(amount)
            tx.mark_success()
        except TravelError as e:
            tx.mark_failed(str(e))
            raise
        return tx

    def get_transaction(self, tx_id: str) -> Transaction:
        return self.transactions[tx_id]


# ===========================
#      GEO / DESTINATION
# ===========================

@dataclass
class Country:
    code: str
    name: str
    currency: str
    airports: List["Airport"] = field(default_factory=list)

    def add_airport(self, airport: "Airport") -> None:
        self.airports.append(airport)

    def find_airport(self, code: str) -> Optional["Airport"]:
        return next((a for a in self.airports if a.code == code), None)


@dataclass
class City:
    name: str
    country: Country
    population: int = 0
    attractions: List[str] = field(default_factory=list)

    def add_attraction(self, name: str) -> None:
        self.attractions.append(name)

    def describe(self) -> str:
        return f"{self.name}, {self.country.name}. Population: {self.population}"


@dataclass
class Destination:
    code: str
    city: City
    description: str
    tags: List[str] = field(default_factory=list)

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


@dataclass
class Airport:
    code: str
    name: str
    city: City
    terminals: List[str] = field(default_factory=list)

    def add_terminal(self, name: str) -> None:
        self.terminals.append(name)

    def full_description(self) -> str:
        return f"{self.name} ({self.code}), {self.city.name}, {self.city.country.code}"


# ===========================
#        FLIGHT DOMAIN
# ===========================

@dataclass
class Seat:
    seat_number: str
    seat_class: str  # Economy, Business
    is_window: bool
    is_occupied: bool = False

    def reserve(self) -> None:
        if self.is_occupied:
            raise SeatUnavailableError(f"Seat {self.seat_number} already occupied")
        self.is_occupied = True

    def free(self) -> None:
        self.is_occupied = False


@dataclass
class PassengerProfile:
    customer: Customer
    passport_number: str
    nationality: str
    date_of_birth: datetime.date
    baggage: List["Baggage"] = field(default_factory=list)

    def add_baggage(self, bag: "Baggage") -> None:
        self.baggage.append(bag)

    def age(self) -> int:
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


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
class Flight:
    flight_number: str
    origin: Airport
    destination: Airport
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    base_price: float
    seats: Dict[str, Seat] = field(default_factory=dict)

    def add_seat(self, seat: Seat) -> None:
        self.seats[seat.seat_number] = seat

    def reserve_seat(self, seat_number: str) -> Seat:
        seat = self.seats.get(seat_number)
        if not seat:
            raise SeatUnavailableError("Seat does not exist")
        seat.reserve()
        return seat

    def available_seats_count(self) -> int:
        return sum(1 for s in self.seats.values() if not s.is_occupied)


# ===========================
#        HOTEL DOMAIN
# ===========================

@dataclass
class RoomType:
    code: str
    name: str
    max_guests: int
    base_price: float

    def price_for_guests(self, guests: int) -> float:
        if guests > self.max_guests:
            raise OverbookingError("Too many guests for this room type")
        return self.base_price + max(0, guests - 1) * (self.base_price * 0.3)


@dataclass
class Room:
    number: str
    room_type: RoomType
    floor: int
    occupied: bool = False

    def occupy(self) -> None:
        if self.occupied:
            raise OverbookingError("Room already occupied")
        self.occupied = True

    def release(self) -> None:
        self.occupied = False


@dataclass
class Hotel:
    name: str
    city: City
    address: str
    rooms: List[Room] = field(default_factory=list)
    rating: float = 0.0

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def find_free_room(self, room_type_code: str) -> Optional[Room]:
        for r in self.rooms:
            if not r.occupied and r.room_type.code == room_type_code:
                return r
        return None

    def update_rating(self, new_rating: float) -> None:
        # примитивное обновление рейтинга
        self.rating = (self.rating + new_rating) / 2 if self.rating else new_rating


# ===========================
#        BOOKINGS
# ===========================

@dataclass
class Booking:
    booking_id: str
    customer: Customer
    created_at: datetime.datetime
    total_price: float
    status: str = "PENDING"  # PENDING, CONFIRMED, CANCELLED
    notes: str = ""

    def confirm(self) -> None:
        self.status = "CONFIRMED"

    def cancel(self) -> None:
        self.status = "CANCELLED"


@dataclass
class FlightBooking(Booking):
    flight: Flight = None
    passenger: PassengerProfile = None
    seat: Optional[Seat] = None
    baggage_fees: float = 0.0

    def assign_seat(self, seat: Seat) -> None:
        self.seat = seat

    def add_baggage_fee(self, amount: float) -> None:
        self.baggage_fees += amount
        self.total_price += amount


@dataclass
class HotelBooking(Booking):
    hotel: Hotel = None
    room: Room = None
    check_in: datetime.date = None
    check_out: datetime.date = None

    def nights(self) -> int:
        return (self.check_out - self.check_in).days

    def extend_stay(self, extra_nights: int) -> None:
        self.check_out += datetime.timedelta(days=extra_nights)


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
        flight_sum = sum(f.base_price for f in self.flights)
        hotel_factor = len(self.hotels) * 50.0
        return self.base_price + flight_sum + hotel_factor


@dataclass
class Itinerary:
    code: str
    customer: Customer
    flight_bookings: List[FlightBooking] = field(default_factory=list)
    hotel_bookings: List[HotelBooking] = field(default_factory=list)

    def add_flight_booking(self, fb: FlightBooking) -> None:
        self.flight_bookings.append(fb)

    def add_hotel_booking(self, hb: HotelBooking) -> None:
        self.hotel_bookings.append(hb)

    def total_cost(self) -> float:
        return sum(b.total_price for b in self.flight_bookings + self.hotel_bookings)


# ===========================
#    LOYALTY / DISCOUNTS
# ===========================

@dataclass
class LoyaltyProgram:
    name: str
    levels: Dict[str, int] = field(default_factory=dict)  # level -> required points
    base_multiplier: float = 1.0

    def add_level(self, level_name: str, required_points: int) -> None:
        self.levels[level_name] = required_points

    def level_for_points(self, points: int) -> str:
        available = [lvl for lvl, req in self.levels.items() if points >= req]
        return max(available, key=lambda l: self.levels[l]) if available else "NONE"


@dataclass
class LoyaltyAccount:
    customer: Customer
    program: LoyaltyProgram
    points: int = 0
    level: str = "NONE"

    def add_points_for_booking(self, booking: Booking) -> None:
        gained = int(booking.total_price * self.program.base_multiplier)
        self.points += gained
        self.level = self.program.level_for_points(self.points)

    def redeem_points(self, amount: int) -> None:
        if amount > self.points:
            raise InsufficientFundsError("Not enough points")
        self.points -= amount


@dataclass
class Coupon:
    code: str
    discount_percent: float
    expires_at: datetime.datetime
    used: bool = False

    def apply(self, total: float) -> float:
        if self.used or datetime.datetime.utcnow() > self.expires_at:
            raise CouponExpiredError("Coupon cannot be used")
        self.used = True
        return total * (1 - self.discount_percent / 100.0)


@dataclass
class Discount:
    name: str
    percent: float
    min_amount: float

    def apply_if_applicable(self, total: float) -> float:
        if total >= self.min_amount:
            return total * (1 - self.percent / 100.0)
        return total


# ===========================
#      CART / SEARCH / REC
# ===========================

@dataclass
class CartItem:
    item_type: str  # FLIGHT, HOTEL, PACKAGE
    reference: object
    price: float
    quantity: int = 1

    def line_total(self) -> float:
        return self.price * self.quantity

    def increase_qty(self, delta: int = 1) -> None:
        self.quantity += delta


@dataclass
class Cart:
    customer: Customer
    items: List[CartItem] = field(default_factory=list)

    def add_item(self, item: CartItem) -> None:
        self.items.append(item)

    def total(self) -> float:
        return sum(i.line_total() for i in self.items)

    def clear(self) -> None:
        self.items.clear()


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


class RecommendationEngine:
    """Тупой, но честный рекомендатор."""

    def __init__(self):
        self.history: Dict[str, List[Destination]] = {}

    def add_history(self, customer: Customer, destination: Destination) -> None:
        self.history.setdefault(customer.user_id, []).append(destination)

    def recommend(self, customer: Customer, all_destinations: List[Destination]) -> List[Destination]:
        """Пример поведения: простейшая рекомендация по тегам."""
        seen = self.history.get(customer.user_id, [])
        seen_tags = {t for d in seen for t in d.tags}
        scored = []
        for dest in all_destinations:
            score = len(seen_tags.intersection(dest.tags))
            scored.append((score, dest))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for score, d in scored if score > 0]


# ===========================
#       NOTIFICATIONS
# ===========================

@dataclass
class Notification:
    notification_id: str
    user: User
    message: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    read: bool = False

    def mark_read(self) -> None:
        self.read = True

    def short(self) -> str:
        return self.message[:40]


@dataclass
class EmailNotification(Notification):
    subject: str = ""
    email_address: str = ""

    def format_email(self) -> str:
        return f"To: {self.email_address}\nSubject: {self.subject}\n\n{self.message}"


@dataclass
class SMSNotification(Notification):
    phone_number: str = ""

    def format_sms(self) -> str:
        return f"SMS to {self.phone_number}: {self.message}"


# ===========================
#     SUPPORT / CHAT
# ===========================

@dataclass
class ChatMessage:
    message_id: str
    author: User
    text: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

    def preview(self) -> str:
        return self.text[:44]


@dataclass
class SupportTicket:
    ticket_id: str
    customer: Customer
    subject: str
    messages: List[ChatMessage] = field(default_factory=list)
    status: str = "OPEN"  # OPEN, CLOSED

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def close(self) -> None:
        self.status = "CLOSED"


# ===========================
#    AUTH / SESSION STUFF
# ===========================

@dataclass
class Session:
    session_id: str
    user: User
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    expires_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=2))

    def is_active(self) -> bool:
        return datetime.datetime.utcnow() < self.expires_at

    def extend(self, hours: int = 1) -> None:
        self.expires_at += datetime.timedelta(hours=hours)


class AuthenticationService:
    """Проверка паролей, создание сессий — всё как ты любишь."""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    @staticmethod
    def hash_password(raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def authenticate(self, user: User, raw_password: str) -> Session:
        if not user.check_password(raw_password):
            raise InvalidPasswordError()
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, user=user)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if not session or not session.is_active():
            raise AuthenticationError("Session expired or not found")
        return session


# ===========================
#       DEMO / USAGE
# ===========================

def demo() -> None:
    # --- Users, auth, cards ---
    print("=== DEMO: simple flow ===")
    auth_service = AuthenticationService()

    # создаём пользователя
    raw_password = "supersecret"
    customer = Customer(
        user_id="cust-1",
        email="user@example.com",
        password_hash=AuthenticationService.hash_password(raw_password),
        full_name="John Traveler",
    )

    # логинимся
    session = auth_service.authenticate(customer, "supersecret")
    print("Session active:", session.is_active())

    # банк и карты
    bank_acc1 = BankAccount(iban="DE001", owner_name="John Traveler", balance=500.0)
    bank_acc2 = BankAccount(iban="DE002", owner_name="Travel Agency", balance=1000.0)

    card1 = PaymentCard(
        card_number="1111 2222 3333 4444",
        owner=customer,
        bank_account=bank_acc1,
        cvv="123",
        expiry_month=12,
        expiry_year=datetime.date.today().year + 1,
        label="Personal card",
    )

    # получатель — некий «агентский» кошелёк
    dummy_owner = Customer(
        user_id="agency",
        email="agency@example.com",
        password_hash=AuthenticationService.hash_password("qwerty"),
        full_name="Best Travel Agency",
    )
    card2 = PaymentCard(
        card_number="5555 6666 7777 8888",
        owner=dummy_owner,
        bank_account=bank_acc2,
        cvv="999",
        expiry_month=12,
        expiry_year=datetime.date.today().year + 1,
        label="Agency card",
    )

    customer.add_card(card1)

    gateway = PaymentGateway(name="DemoPay")

    # --- Geography, airports, flight ---
    country1 = Country(code="DE", name="Germany", currency="EUR")
    country2 = Country(code="ES", name="Spain", currency="EUR")

    city_berlin = City(name="Berlin", country=country1, population=3_600_000)
    city_madrid = City(name="Madrid", country=country2, population=3_200_000)

    airport_ber = Airport(code="BER", name="Berlin Brandenburg", city=city_berlin)
    airport_mad = Airport(code="MAD", name="Madrid-Barajas", city=city_madrid)

    country1.add_airport(airport_ber)
    country2.add_airport(airport_mad)

    departure = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    arrival = departure + datetime.timedelta(hours=3)

    flight = Flight(
        flight_number="BT123",
        origin=airport_ber,
        destination=airport_mad,
        departure_time=departure,
        arrival_time=arrival,
        base_price=150.0,
    )

    # добавим пару мест
    flight.add_seat(Seat(seat_number="12A", seat_class="Economy", is_window=True))
    flight.add_seat(Seat(seat_number="12B", seat_class="Economy", is_window=False))

    # --- Passenger profile, baggage ---
    passenger = PassengerProfile(
        customer=customer,
        passport_number="X1234567",
        nationality="DE",
        date_of_birth=datetime.date(1995, 5, 10),
    )

    bag = Baggage(tag="BAG001", weight_kg=23.0)
    passenger.add_baggage(bag)
    fee = bag.overweight_fee(limit=20.0, fee_per_kg=10.0)
    print("Baggage overweight fee:", fee)

    # --- Booking flight ---
    seat = flight.reserve_seat("12A")

    booking_id = str(uuid.uuid4())
    flight_booking = FlightBooking(
        booking_id=booking_id,
        customer=customer,
        created_at=datetime.datetime.utcnow(),
        total_price=flight.base_price + fee,
        flight=flight,
        passenger=passenger,
    )
    flight_booking.assign_seat(seat)
    flight_booking.add_baggage_fee(fee)
    flight_booking.confirm()

    print("Flight booking total price:", flight_booking.total_price)

    # --- Payment: card1 -> card2 ---
    print("Balances before:", bank_acc1.balance, bank_acc2.balance)
    try:
        tx = gateway.transfer(from_card=card1, to_card=card2, amount=flight_booking.total_price)
        print("Transaction status:", tx.status)
    except TravelError as e:
        print("Payment failed:", e)

    print("Balances after:", bank_acc1.balance, bank_acc2.balance)

    # --- Loyalty program ---
    program = LoyaltyProgram(name="SkyPoints", base_multiplier=1.5)
    program.add_level("SILVER", 500)
    program.add_level("GOLD", 1500)

    loyalty_acc = LoyaltyAccount(customer=customer, program=program)
    customer.loyalty_account = loyalty_acc

    loyalty_acc.add_points_for_booking(flight_booking)
    print("Loyalty points:", loyalty_acc.points, "level:", loyalty_acc.level)

    # --- Coupon / discount ---
    coupon = Coupon(
        code="WELCOME10",
        discount_percent=10.0,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=1),
    )
    discounted = coupon.apply(flight_booking.total_price)
    print("Price with coupon:", discounted)

    # --- Cart ---
    cart = Cart(customer=customer)
    cart.add_item(CartItem(item_type="FLIGHT", reference=flight_booking, price=discounted))
    print("Cart total:", cart.total())

    # --- Notification ---
    notif = EmailNotification(
        notification_id=str(uuid.uuid4()),
        user=customer,
        message=f"Your booking {flight_booking.booking_id} is confirmed.",
        subject="Booking confirmation",
        email_address=customer.email,
    )
    print("Email preview:\n", notif.format_email()[:100], "...")


if __name__ == "__main__":
    # Да, тут нет юнит-тестов, тут просто проверка что всё вообще живое.
    demo()
