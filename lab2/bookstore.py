from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict
import hashlib
import uuid



# Custom Exceptions (12x)


class BookNotFoundError(Exception):
    pass


class OutOfStockError(Exception):
    pass


class DuplicateISBNError(Exception):
    pass


class InvalidISBNError(Exception):
    pass


class CustomerNotFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class PaymentDeclinedError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class UnauthorizedAccessError(Exception):
    pass


class WarehouseCapacityError(Exception):
    pass


class OrderStateError(Exception):
    pass


class LoyaltyPointsError(Exception):
    pass



# Value Objects & Basics


@dataclass
class Currency:
    code: str
    symbol: str
    name: str

    def format_amount(self, amount: float) -> str:
        return f"{self.symbol}{amount:,.2f}"

    def is_same(self, other: "Currency") -> bool:
        return self.code == other.code


@dataclass
class Money:
    amount: float
    currency: Currency

    def add(self, other: "Money") -> "Money":
        if self.currency.code != other.currency.code:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: "Money") -> "Money":
        if self.currency.code != other.currency.code:
            raise ValueError("Currency mismatch")
        result = self.amount - other.amount
        if result < 0:
            raise InsufficientFundsError("Not enough money to subtract")
        return Money(result, self.currency)

    def is_positive(self) -> bool:
        return self.amount > 0

    def multiply(self, factor: float) -> "Money":
        return Money(self.amount * factor, self.currency)

    def as_tuple(self) -> tuple:
        return self.amount, self.currency.code


@dataclass
class Address:
    line1: str
    city: str
    country: str
    postal_code: str

    def format(self) -> str:
        return f"{self.line1}, {self.postal_code} {self.city}, {self.country}"

    def city_country(self) -> str:
        return f"{self.city}, {self.country}"

    def change_city(self, new_city: str) -> None:
        self.city = new_city


@dataclass
class Email:
    value: str

    def is_valid(self) -> bool:
        return "@" in self.value and "." in self.value.split("@")[-1]

    def domain(self) -> str:
        return self.value.split("@")[-1] if "@" in self.value else ""


@dataclass
class PhoneNumber:
    value: str

    def normalized(self) -> str:
        return "".join(ch for ch in self.value if ch.isdigit())

    def starts_with_plus(self) -> bool:
        return self.value.strip().startswith("+")


@dataclass
class PersonName:
    first_name: str
    last_name: str

    def full(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def initials(self) -> str:
        return f"{self.first_name[0]}.{self.last_name[0]}."


@dataclass
class ISBN:
    value: str

    def __post_init__(self) -> None:
        if not self._basic_check():
            raise InvalidISBNError(f"Invalid ISBN: {self.value}")

    def _basic_check(self) -> bool:
        digits = [c for c in self.value if c.isdigit()]
        return len(digits) in (10, 13)

    def normalized(self) -> str:
        return "".join(ch for ch in self.value if ch.isdigit())

    def is_isbn13(self) -> bool:
        return len(self.normalized()) == 13


@dataclass
class BookId:
    value: str

    @staticmethod
    def new() -> "BookId":
        return BookId(str(uuid.uuid4()))

    def short(self) -> str:
        return self.value.split("-")[0]



# Book Domain


@dataclass
class Author:
    id: str
    name: PersonName
    biography: str = ""

    def short_bio(self) -> str:
        return (self.biography[:75] + "...") if len(self.biography) > 75 else self.biography

    def pen_name(self) -> str:
        return self.name.full()


@dataclass
class Publisher:
    id: str
    name: str
    address: Optional[Address] = None

    def update_address(self, address: Address) -> None:
        self.address = address

    def has_address(self) -> bool:
        return self.address is not None


@dataclass
class Category:
    code: str
    name: str
    description: str = ""

    def matches(self, text: str) -> bool:
        return text.lower() in self.name.lower() or text.lower() in self.description.lower()

    def is_code(self, code: str) -> bool:
        return self.code == code


@dataclass
class Tag:
    name: str

    def slug(self) -> str:
        return self.name.lower().replace(" ", "-")

    def is_same(self, other: "Tag") -> bool:
        return self.slug() == other.slug()


@dataclass
class Book:
    id: BookId
    title: str
    author: Author
    publisher: Publisher
    isbn: ISBN
    categories: List[Category] = field(default_factory=list)
    tags: List[Tag] = field(default_factory=list)
    base_price: Money = field(default=None)

    def add_category(self, category: Category) -> None:
        if category not in self.categories:
            self.categories.append(category)

    def add_tag(self, tag: Tag) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def current_price(self, discount_percent: float = 0.0) -> Money:
        if discount_percent <= 0:
            return self.base_price
        discount_amount = self.base_price.amount * discount_percent / 100
        return Money(self.base_price.amount - discount_amount, self.base_price.currency)

    def matches_title(self, text: str) -> bool:
        return text.lower() in self.title.lower()


@dataclass
class BookCopy:
    copy_id: str
    book: Book
    condition: str
    is_reserved: bool = False

    def reserve(self) -> None:
        if self.is_reserved:
            raise OutOfStockError("Copy already reserved")
        self.is_reserved = True

    def release(self) -> None:
        self.is_reserved = False

    def is_available(self) -> bool:
        return not self.is_reserved



# Warehouse & Inventory


@dataclass
class Shelf:
    id: str
    label: str
    max_capacity: int
    copies: List[BookCopy] = field(default_factory=list)

    def add_copy(self, copy: BookCopy) -> None:
        if len(self.copies) >= self.max_capacity:
            raise WarehouseCapacityError("Shelf is full")
        self.copies.append(copy)

    def available_copies(self) -> List[BookCopy]:
        return [c for c in self.copies if not c.is_reserved]

    def utilization(self) -> float:
        if self.max_capacity == 0:
            return 0.0
        return len(self.copies) / self.max_capacity


@dataclass
class Aisle:
    id: str
    name: str
    shelves: List[Shelf] = field(default_factory=list)

    def add_shelf(self, shelf: Shelf) -> None:
        self.shelves.append(shelf)

    def find_shelf(self, label: str) -> Optional[Shelf]:
        for shelf in self.shelves:
            if shelf.label == label:
                return shelf
        return None

    def shelf_count(self) -> int:
        return len(self.shelves)


@dataclass
class WarehouseLocation:
    code: str
    description: str
    address: Address

    def full_label(self) -> str:
        return f"{self.code} - {self.description}"

    def same_place(self, other: "WarehouseLocation") -> bool:
        return self.code == other.code


@dataclass
class StockItem:
    book: Book
    quantity: int
    location: WarehouseLocation

    def increase(self, amount: int) -> None:
        self.quantity += amount

    def decrease(self, amount: int) -> None:
        if amount > self.quantity:
            raise OutOfStockError("Not enough stock to decrease")
        self.quantity -= amount

    def is_empty(self) -> bool:
        return self.quantity == 0


@dataclass
class Inventory:
    items: Dict[str, StockItem] = field(default_factory=dict)

    def add_book(self, book: Book, location: WarehouseLocation, quantity: int) -> None:
        if book.isbn.value in self.items:
            self.items[book.isbn.value].increase(quantity)
        else:
            self.items[book.isbn.value] = StockItem(book=book, quantity=quantity, location=location)

    def reserve_book(self, isbn: ISBN, quantity: int) -> None:
        key = isbn.value
        if key not in self.items:
            raise BookNotFoundError(f"ISBN {isbn.value} not found in inventory")
        self.items[key].decrease(quantity)

    def available_quantity(self, isbn: ISBN) -> int:
        item = self.items.get(isbn.value)
        return item.quantity if item else 0

    def has_book(self, isbn: ISBN) -> bool:
        return isbn.value in self.items


@dataclass
class Warehouse:
    id: str
    name: str
    location: WarehouseLocation
    aisles: List[Aisle] = field(default_factory=list)
    inventory: Inventory = field(default_factory=Inventory)

    def add_aisle(self, aisle: Aisle) -> None:
        self.aisles.append(aisle)

    def total_titles(self) -> int:
        return len(self.inventory.items)

    def total_stock(self) -> int:
        return sum(item.quantity for item in self.inventory.items.values())



# Customers & Accounts


@dataclass
class CustomerId:
    value: str

    @staticmethod
    def new() -> "CustomerId":
        return CustomerId(str(uuid.uuid4()))

    def short(self) -> str:
        return self.value.split("-")[0]


@dataclass
class PasswordHash:
    hash_value: str

    @staticmethod
    def from_plain(password: str) -> "PasswordHash":
        h = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return PasswordHash(h)

    def verify(self, password: str) -> bool:
        return self.hash_value == hashlib.sha256(password.encode("utf-8")).hexdigest()

    def change_password(self, old: str, new: str) -> "PasswordHash":
        if not self.verify(old):
            raise InvalidPasswordError("Wrong password")
        return PasswordHash.from_plain(new)


@dataclass
class LoyaltyTier:
    name: str
    discount_percent: float
    required_points: int

    def qualifies(self, points: int) -> bool:
        return points >= self.required_points

    def better_than(self, other: "LoyaltyTier") -> bool:
        return self.discount_percent > other.discount_percent


@dataclass
class LoyaltyAccount:
    customer_id: CustomerId
    points: int = 0
    tier: Optional[LoyaltyTier] = None

    def add_points(self, points: int) -> None:
        if points < 0:
            raise LoyaltyPointsError("Cannot add negative points")
        self.points += points

    def apply_tier(self, tiers: List[LoyaltyTier]) -> None:
        best = None
        for tier in tiers:
            if tier.qualifies(self.points):
                if best is None or tier.discount_percent > best.discount_percent:
                    best = tier
        self.tier = best

    def current_discount(self) -> float:
        return self.tier.discount_percent if self.tier else 0.0


@dataclass
class CustomerAccount:
    id: CustomerId
    name: PersonName
    email: Email
    address: Address
    password_hash: PasswordHash
    loyalty: LoyaltyAccount

    def check_password(self, password: str) -> None:
        if not self.password_hash.verify(password):
            raise InvalidPasswordError("Wrong password")

    def change_email(self, new_email: Email) -> None:
        if not new_email.is_valid():
            raise ValueError("Invalid email")
        self.email = new_email

    def add_loyalty_points_for_order(self, amount: Money) -> None:
        points = int(amount.amount)
        self.loyalty.add_points(points)


@dataclass
class CartItem:
    book: Book
    quantity: int

    def line_total(self) -> Money:
        price = self.book.current_price()
        return Money(price.amount * self.quantity, price.currency)

    def increase(self, by: int = 1) -> None:
        self.quantity += by


@dataclass
class ShoppingCart:
    customer_id: CustomerId
    items: List[CartItem] = field(default_factory=list)

    def add_item(self, book: Book, quantity: int = 1) -> None:
        for item in self.items:
            if item.book.id.value == book.id.value:
                item.quantity += quantity
                return
        self.items.append(CartItem(book=book, quantity=quantity))

    def total(self) -> Money:
        if not self.items:
            # Assume default currency USD for empty cart
            currency = Currency(code="USD", symbol="$", name="US Dollar")
            return Money(0.0, currency)
        currency = self.items[0].book.base_price.currency
        amount = sum(item.line_total().amount for item in self.items)
        return Money(amount, currency)

    def clear(self) -> None:
        self.items.clear()



# Orders & Payments


@dataclass
class OrderId:
    value: str

    @staticmethod
    def new() -> "OrderId":
        return OrderId(str(uuid.uuid4()))

    def short(self) -> str:
        return self.value.split("-")[0]


@dataclass
class OrderLine:
    book: Book
    quantity: int
    unit_price: Money

    def line_total(self) -> Money:
        return Money(self.unit_price.amount * self.quantity, self.unit_price.currency)

    def describe(self) -> str:
        return f"{self.book.title} x{self.quantity}"


@dataclass
class Order:
    id: OrderId
    customer: CustomerAccount
    lines: List[OrderLine]
    created_at: datetime
    status: str = "NEW"

    def total(self) -> Money:
        currency = self.lines[0].unit_price.currency
        amount = sum(line.line_total().amount for line in self.lines)
        return Money(amount, currency)

    def mark_paid(self) -> None:
        if self.status != "NEW":
            raise OrderStateError("Order is not in NEW state")
        self.status = "PAID"

    def cancel(self) -> None:
        if self.status == "PAID":
            raise OrderStateError("Cannot cancel paid order")
        self.status = "CANCELLED"

    def is_open(self) -> bool:
        return self.status in ("NEW", "PAID")


@dataclass
class PaymentCard:
    card_number: str
    holder_name: PersonName
    expiry_month: int
    expiry_year: int
    balance: Money

    def is_valid(self, on_date: date) -> bool:
        return (self.expiry_year, self.expiry_month) >= (on_date.year, on_date.month)

    def charge(self, amount: Money, on_date: date) -> None:
        if not self.is_valid(on_date):
            raise PaymentDeclinedError("Card expired")
        self.balance = self.balance.subtract(amount)

    def credit(self, amount: Money) -> None:
        self.balance = self.balance.add(amount)


@dataclass
class PaymentTransaction:
    id: str
    from_card: PaymentCard
    to_card: PaymentCard
    amount: Money
    created_at: datetime
    status: str = "PENDING"

    def complete(self) -> None:
        if self.status != "PENDING":
            raise PaymentDeclinedError("Transaction already processed")
        self.from_card.charge(self.amount, date.today())
        self.to_card.credit(self.amount)
        self.status = "COMPLETED"

    def fail(self, reason: str) -> None:
        self.status = f"FAILED: {reason}"

    def is_successful(self) -> bool:
        return self.status == "COMPLETED"


@dataclass
class PaymentGateway:
    name: str

    def transfer(self, from_card: PaymentCard, to_card: PaymentCard, amount: Money) -> PaymentTransaction:
        tx = PaymentTransaction(
            id=str(uuid.uuid4()),
            from_card=from_card,
            to_card=to_card,
            amount=amount,
            created_at=datetime.utcnow(),
        )
        tx.complete()
        return tx

    def refund(self, from_card: PaymentCard, to_card: PaymentCard, amount: Money) -> PaymentTransaction:
        # reverse direction for refund
        return self.transfer(from_card=to_card, to_card=from_card, amount=amount)


@dataclass
class Invoice:
    id: str
    order: Order
    issued_at: datetime
    total: Money

    def mark_paid(self) -> None:
        self.order.mark_paid()

    def is_overdue(self, on_date: date) -> bool:
        return (on_date - self.issued_at.date()).days > 30 and self.order.status != "PAID"


@dataclass
class DiscountCode:
    code: str
    percent: float
    active: bool = True

    def apply(self, total: Money) -> Money:
        if not self.active:
            return total
        discount = total.amount * self.percent / 100
        return Money(total.amount - discount, total.currency)

    def deactivate(self) -> None:
        self.active = False



# Shipping & Logistics


@dataclass
class DeliveryMethod:
    code: str
    name: str
    price: Money

    def is_free(self) -> bool:
        return self.price.amount == 0

    def label(self) -> str:
        return f"{self.name} ({self.price.currency.symbol}{self.price.amount})"


@dataclass
class ShipmentTracking:
    code: str
    status: str
    history: List[str] = field(default_factory=list)

    def add_event(self, event: str) -> None:
        self.history.append(event)
        self.status = event

    def last_event(self) -> Optional[str]:
        return self.history[-1] if self.history else None


@dataclass
class Shipment:
    id: str
    order: Order
    method: DeliveryMethod
    tracking: ShipmentTracking
    shipped_at: Optional[datetime] = None

    def ship(self) -> None:
        self.shipped_at = datetime.utcnow()
        self.tracking.add_event("Shipped")

    def is_shipped(self) -> bool:
        return self.shipped_at is not None


@dataclass
class Reservation:
    id: str
    book: Book
    customer: CustomerAccount
    expires_at: datetime
    active: bool = True

    def expire(self) -> None:
        self.active = False

    def is_active(self) -> bool:
        return self.active and datetime.utcnow() < self.expires_at



# Suppliers & Purchasing


@dataclass
class Supplier:
    id: str
    name: str
    contact_email: Email

    def contact(self, message: str) -> str:
        return f"Email sent to {self.contact_email.value}: {message}"

    def labeled(self) -> str:
        return f"{self.name} <{self.contact_email.value}>"


@dataclass
class PurchaseOrder:
    id: str
    supplier: Supplier
    items: List[StockItem]
    created_at: datetime
    status: str = "OPEN"

    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    def close(self) -> None:
        self.status = "CLOSED"

    def is_open(self) -> bool:
        return self.status == "OPEN"


@dataclass
class ReturnRequest:
    id: str
    order: Order
    reason: str
    created_at: datetime
    approved: bool = False

    def approve(self) -> None:
        self.approved = True

    def reject(self) -> None:
        self.approved = False

    def is_pending(self) -> bool:
        return not self.approved



# Reviews & Notifications


@dataclass
class Review:
    id: str
    book: Book
    customer: CustomerAccount
    rating: int
    comment: str

    def is_positive(self) -> bool:
        return self.rating >= 4

    def short_comment(self) -> str:
        return (self.comment[:40] + "...") if len(self.comment) > 40 else self.comment


@dataclass
class NotificationChannel:
    code: str
    description: str

    def send(self, notification: "Notification") -> str:
        return f"Sent via {self.code}: {notification.message}"

    def label(self) -> str:
        return f"{self.code} - {self.description}"


@dataclass
class Notification:
    id: str
    customer: CustomerAccount
    message: str
    channel: NotificationChannel
    created_at: datetime

    def dispatch(self) -> str:
        return self.channel.send(self)

    def preview(self) -> str:
        return self.message[:20]



# Security & Auditing


@dataclass
class AuditLogEntry:
    id: str
    actor: str
    action: str
    created_at: datetime
    details: str

    def summary(self) -> str:
        return f"[{self.created_at.isoformat()}] {self.actor}: {self.action}"

    def detailed(self) -> str:
        return f"{self.summary()} -> {self.details}"


@dataclass
class AccessPolicy:
    name: str
    allowed_actions: List[str]

    def can(self, action: str) -> bool:
        return action in self.allowed_actions

    def add_action(self, action: str) -> None:
        if action not in self.allowed_actions:
            self.allowed_actions.append(action)


@dataclass
class UserSession:
    id: str
    customer: CustomerAccount
    policy: AccessPolicy
    created_at: datetime
    active: bool = True

    def ensure_can(self, action: str) -> None:
        if not self.policy.can(action):
            raise UnauthorizedAccessError(f"Action '{action}' not allowed")

    def terminate(self) -> None:
        self.active = False

    def is_active(self) -> bool:
        return self.active



# Reporting & Search


@dataclass
class ReportGenerator:
    name: str

    def generate_sales_report(self, orders: List[Order]) -> Dict[str, float]:
        report: Dict[str, float] = {}
        for order in orders:
            for line in order.lines:
                title = line.book.title
                report[title] = report.get(title, 0.0) + line.line_total().amount
        return report

    def top_selling_titles(self, report: Dict[str, float], limit: int = 5) -> List[str]:
        return sorted(report, key=report.get, reverse=True)[:limit]

    def total_revenue(self, report: Dict[str, float]) -> float:
        return sum(report.values())


@dataclass
class BookSearchEngine:
    name: str
    index: Dict[str, Book] = field(default_factory=dict)

    def index_book(self, book: Book) -> None:
        self.index[book.title.lower()] = book

    def search_by_title(self, query: str) -> List[Book]:
        q = query.lower()
        return [book for title, book in self.index.items() if q in title]

    def clear(self) -> None:
        self.index.clear()


if __name__ == "__main__":
    # Минимальный смоук-тест, чтобы не выглядеть совсем как учебный труп
    usd = Currency(code="USD", symbol="$", name="US Dollar")
    addr = Address(line1="Warehouse street 1", city="Booktown", country="DE", postal_code="12345")
    loc = WarehouseLocation(code="WH1", description="Main warehouse", address=addr)
    publisher = Publisher(id="pub1", name="NoName Publishing")
    author = Author(id="auth1", name=PersonName("John", "Doe"))
    book = Book(
        id=BookId.new(),
        title="Sample Book",
        author=author,
        publisher=publisher,
        isbn=ISBN("9780306406157"),
        base_price=Money(10.0, usd),
    )
    inventory = Inventory()
    inventory.add_book(book, loc, quantity=10)
    print("Available:", inventory.available_quantity(book.isbn))
