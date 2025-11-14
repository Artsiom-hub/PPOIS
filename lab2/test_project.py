import unittest
from datetime import date
import uuid
from bookstore import *
# тут импортируешь свои классы
# from book_store import (
#     Currency, Money, Address, Email, PhoneNumber, PersonName,
#     ISBN, BookId, Author, Publisher,
#     InvalidISBNError, InsufficientFundsError
# )

# Для примера — копия исключений, чтобы тест-файл был самодостаточным.
# У себя бери реальные.
class InvalidISBNError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class Currency:
    def __init__(self, code: str, symbol: str, name: str):
        self.code = code
        self.symbol = symbol
        self.name = name

    def format_amount(self, amount: float) -> str:
        return f"{self.symbol}{amount:,.2f}"

    def is_same(self, other: "Currency") -> bool:
        return self.code == other.code


class Money:
    def __init__(self, amount: float, currency: Currency):
        self.amount = amount
        self.currency = currency

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


class Address:
    def __init__(self, line1: str, city: str, country: str, postal_code: str):
        self.line1 = line1
        self.city = city
        self.country = country
        self.postal_code = postal_code

    def format(self) -> str:
        return f"{self.line1}, {self.postal_code} {self.city}, {self.country}"

    def city_country(self) -> str:
        return f"{self.city}, {self.country}"

    def change_city(self, new_city: str) -> None:
        self.city = new_city


class Email:
    def __init__(self, value: str):
        self.value = value

    def is_valid(self) -> bool:
        return "@" in self.value and "." in self.value.split("@")[-1]

    def domain(self) -> str:
        return self.value.split("@")[-1] if "@" in self.value else ""


class PhoneNumber:
    def __init__(self, value: str):
        self.value = value

    def normalized(self) -> str:
        return "".join(ch for ch in self.value if ch.isdigit())

    def starts_with_plus(self) -> bool:
        return self.value.strip().startswith("+")


class PersonName:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    def full(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def initials(self) -> str:
        return f"{self.first_name[0]}.{self.last_name[0]}."


class ISBN:
    def __init__(self, value: str):
        self.value = value
        if not self._basic_check():
            raise InvalidISBNError(f"Invalid ISBN: {self.value}")

    def _basic_check(self) -> bool:
        digits = [c for c in self.value if c.isdigit()]
        return len(digits) in (10, 13)

    def normalized(self) -> str:
        return "".join(ch for ch in self.value if ch.isdigit())

    def is_isbn13(self) -> bool:
        return len(self.normalized()) == 13


class BookId:
    def __init__(self, value: str):
        self.value = value

    @staticmethod
    def new() -> "BookId":
        return BookId(str(uuid.uuid4()))

    def short(self) -> str:
        return self.value.split("-")[0]


class Author:
    def __init__(self, id: str, name: PersonName, biography: str = ""):
        self.id = id
        self.name = name
        self.biography = biography

    def short_bio(self) -> str:
        return (self.biography[:75] + "...") if len(self.biography) > 75 else self.biography

    def pen_name(self) -> str:
        return self.name.full()


class Publisher:
    def __init__(self, id: str, name: str, address=None):
        self.id = id
        self.name = name
        self.address = address

    def update_address(self, address: Address) -> None:
        self.address = address

    def has_address(self) -> bool:
        return self.address is not None


# ============================
#   TESTS
# ============================

class TestCurrency(unittest.TestCase):

    def test_format_amount_basic(self):
        cur = Currency(code="USD", symbol="$", name="US Dollar")
        self.assertEqual(cur.format_amount(10), "$10.00")
        self.assertEqual(cur.format_amount(1234.5), "$1,234.50")

    def test_is_same_true_and_false(self):
        c1 = Currency("USD", "$", "US Dollar")
        c2 = Currency("USD", "$", "US Dollar")
        c3 = Currency("EUR", "€", "Euro")
        self.assertTrue(c1.is_same(c2))
        self.assertFalse(c1.is_same(c3))


class TestMoney(unittest.TestCase):

    def setUp(self):
        self.usd = Currency("USD", "$", "US Dollar")
        self.eur = Currency("EUR", "€", "Euro")

    def test_add_same_currency(self):
        m1 = Money(10, self.usd)
        m2 = Money(5, self.usd)
        result = m1.add(m2)
        self.assertEqual(result.amount, 15)
        self.assertIs(result.currency, self.usd)

    def test_add_different_currency_raises(self):
        m1 = Money(10, self.usd)
        m2 = Money(5, self.eur)
        with self.assertRaises(ValueError):
            m1.add(m2)

    def test_subtract_ok(self):
        m1 = Money(10, self.usd)
        m2 = Money(4, self.usd)
        result = m1.subtract(m2)
        self.assertEqual(result.amount, 6)

    def test_subtract_to_zero(self):
        m1 = Money(10, self.usd)
        m2 = Money(10, self.usd)
        result = m1.subtract(m2)
        self.assertEqual(result.amount, 0)

    def test_subtract_negative_raises_insufficient(self):
        m1 = Money(5, self.usd)
        m2 = Money(10, self.usd)
        with self.assertRaises(InsufficientFundsError):
            m1.subtract(m2)

    def test_subtract_different_currency_raises(self):
        m1 = Money(10, self.usd)
        m2 = Money(1, self.eur)
        with self.assertRaises(ValueError):
            m1.subtract(m2)

    def test_is_positive(self):
        self.assertTrue(Money(1, self.usd).is_positive())
        self.assertFalse(Money(0, self.usd).is_positive())
        self.assertFalse(Money(-1, self.usd).is_positive())

    def test_multiply(self):
        m = Money(10, self.usd)
        result = m.multiply(2.5)
        self.assertEqual(result.amount, 25)
        self.assertIs(result.currency, self.usd)

    def test_as_tuple(self):
        m = Money(10.5, self.usd)
        self.assertEqual(m.as_tuple(), (10.5, "USD"))


class TestAddress(unittest.TestCase):

    def test_format_and_city_country(self):
        addr = Address("Main st 1", "Berlin", "DE", "12345")
        self.assertEqual(addr.format(), "Main st 1, 12345 Berlin, DE")
        self.assertEqual(addr.city_country(), "Berlin, DE")

    def test_change_city(self):
        addr = Address("Main st 1", "Berlin", "DE", "12345")
        addr.change_city("Munich")
        self.assertEqual(addr.city, "Munich")
        self.assertEqual(addr.city_country(), "Munich, DE")


class TestEmail(unittest.TestCase):

    def test_is_valid_true(self):
        e = Email("user@example.com")
        self.assertTrue(e.is_valid())

    def test_is_valid_false(self):
        self.assertFalse(Email("userexample.com").is_valid())
        self.assertFalse(Email("user@com").is_valid())

    def test_domain(self):
        e = Email("user@example.com")
        self.assertEqual(e.domain(), "example.com")
        self.assertEqual(Email("bademail").domain(), "")


class TestPhoneNumber(unittest.TestCase):

    def test_normalized(self):
        p = PhoneNumber("+1 (234) 567-89-00")
        self.assertEqual(p.normalized(), "12345678900")

    def test_starts_with_plus(self):
        self.assertTrue(PhoneNumber(" +123").starts_with_plus())
        self.assertFalse(PhoneNumber("123").starts_with_plus())


class TestPersonName(unittest.TestCase):

    def test_full_and_initials(self):
        n = PersonName("John", "Doe")
        self.assertEqual(n.full(), "John Doe")
        self.assertEqual(n.initials(), "J.D.")


class TestISBN(unittest.TestCase):

    def test_valid_isbn10(self):
        i = ISBN("0-306-40615-2")
        self.assertEqual(i.normalized(), "0306406152")
        self.assertFalse(i.is_isbn13())

    def test_valid_isbn13(self):
        i = ISBN("978-0-306-40615-7")
        self.assertEqual(i.normalized(), "9780306406157")
        self.assertTrue(i.is_isbn13())

    def test_invalid_isbn_raises(self):
        with self.assertRaises(InvalidISBNError):
            ISBN("123")  # слишком короткий
        with self.assertRaises(InvalidISBNError):
            ISBN("abcdefghijk")  # буквенный бред

    def test_basic_check_private_logic(self):
        # просто sanity-check, что странный формат с 13 цифрами всё ещё ок
        i = ISBN("ISBN 978 0 306 40615 7")
        self.assertTrue(i.is_isbn13())


class TestBookId(unittest.TestCase):

    def test_new_generates_non_empty_and_unique(self):
        b1 = BookId.new()
        b2 = BookId.new()
        self.assertIsInstance(b1, BookId)
        self.assertIsInstance(b2, BookId)
        self.assertNotEqual(b1.value, "")
        self.assertNotEqual(b1.value, b2.value)

    def test_short(self):
        b = BookId("abcd-1234-xyz")
        self.assertEqual(b.short(), "abcd")
        b2 = BookId("nohyphen")
        self.assertEqual(b2.short(), "nohyphen")


class TestAuthor(unittest.TestCase):

    def test_short_bio_short(self):
        name = PersonName("John", "Doe")
        a = Author(id="1", name=name, biography="Short bio")
        self.assertEqual(a.short_bio(), "Short bio")

    def test_short_bio_truncated(self):
        name = PersonName("John", "Doe")
        long_text = "X" * 80
        a = Author(id="1", name=name, biography=long_text)
        result = a.short_bio()
        self.assertTrue(result.endswith("..."))
        self.assertLessEqual(len(result), 78)

    def test_pen_name(self):
        name = PersonName("John", "Doe")
        a = Author(id="1", name=name)
        self.assertEqual(a.pen_name(), "John Doe")


class TestPublisher(unittest.TestCase):

    def test_has_address_false_by_default(self):
        p = Publisher(id="1", name="TestPub")
        self.assertFalse(p.has_address())

    def test_update_address_and_has_address_true(self):
        p = Publisher(id="1", name="TestPub")
        addr = Address("Main st 1", "Berlin", "DE", "12345")
        p.update_address(addr)
        self.assertTrue(p.has_address())
        self.assertIs(p.address, addr)

class TestCategory(unittest.TestCase):

    def test_matches_name_and_description(self):
        c = Category(code="FIC", name="Fiction", description="Stories and novels")
        self.assertTrue(c.matches("fic"))
        self.assertTrue(c.matches("Stories"))
        self.assertFalse(c.matches("biology"))

    def test_is_code(self):
        c = Category("SCI", "Science")
        self.assertTrue(c.is_code("SCI"))
        self.assertFalse(c.is_code("FIC"))


class TestTag(unittest.TestCase):

    def test_slug_generation(self):
        t = Tag("Dark Fantasy")
        self.assertEqual(t.slug(), "dark-fantasy")

    def test_is_same(self):
        t1 = Tag("Sci Fi")
        t2 = Tag("sci-fi")
        self.assertTrue(t1.is_same(t2))
        self.assertTrue(t2.is_same(t1))
        t3 = Tag("Fantasy")
        self.assertFalse(t1.is_same(t3))


class TestBook(unittest.TestCase):

    def setUp(self):
        self.usd = Currency("USD", "$", "US Dollar")
        self.publisher = Publisher("1", "Pub")
        self.author = Author("A1", PersonName("John", "Doe"))
        self.book = Book(
            id=BookId("id1"),
            title="The Great Story",
            author=self.author,
            publisher=self.publisher,
            isbn=ISBN("9780306406157"),
            base_price=Money(100, self.usd),
        )

    def test_add_category_no_duplicates(self):
        c1 = Category("FIC", "Fiction")
        self.book.add_category(c1)
        self.book.add_category(c1)
        self.assertEqual(len(self.book.categories), 1)

    def test_add_tag_no_duplicates(self):
        t = Tag("Epic")
        self.book.add_tag(t)
        self.book.add_tag(t)
        self.assertEqual(len(self.book.tags), 1)

    def test_current_price_no_discount(self):
        price = self.book.current_price()
        self.assertEqual(price.amount, 100)

    def test_current_price_with_discount(self):
        price = self.book.current_price(10)  # 10%
        self.assertEqual(price.amount, 90)

    def test_matches_title(self):
        self.assertTrue(self.book.matches_title("great"))
        self.assertFalse(self.book.matches_title("banana"))


class TestBookCopy(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "US Dollar")
        book = Book(
            id=BookId("b1"),
            title="Test",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd),
        )
        self.copy = BookCopy("C1", book, "Good")

    def test_reserve_and_release(self):
        self.assertTrue(self.copy.is_available())
        self.copy.reserve()
        self.assertFalse(self.copy.is_available())
        self.copy.release()
        self.assertTrue(self.copy.is_available())

    def test_double_reserve_raises(self):
        self.copy.reserve()
        with self.assertRaises(OutOfStockError):
            self.copy.reserve()


class TestShelf(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "USD")
        book = Book(
            id=BookId("b1"),
            title="Test",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd),
        )
        self.copy = BookCopy("C1", book, "Good")
        self.shelf = Shelf("S1", "A1", max_capacity=1)

    def test_add_copy(self):
        self.shelf.add_copy(self.copy)
        self.assertEqual(len(self.shelf.copies), 1)

    def test_add_copy_overflow(self):
        self.shelf.add_copy(self.copy)
        with self.assertRaises(WarehouseCapacityError):
            self.shelf.add_copy(self.copy)

    def test_available_copies(self):
        self.shelf.add_copy(self.copy)
        self.assertEqual(len(self.shelf.available_copies()), 1)
        self.copy.reserve()
        self.assertEqual(len(self.shelf.available_copies()), 0)

    def test_utilization(self):
        self.assertEqual(self.shelf.utilization(), 0.0)
        self.shelf.add_copy(self.copy)
        self.assertEqual(self.shelf.utilization(), 1.0)


class TestAisle(unittest.TestCase):

    def test_add_and_find_shelf(self):
        aisle = Aisle("1", "Main")
        shelf = Shelf("S1", "A1", 5)
        aisle.add_shelf(shelf)
        self.assertEqual(aisle.shelf_count(), 1)
        self.assertIs(aisle.find_shelf("A1"), shelf)
        self.assertIsNone(aisle.find_shelf("Nope"))


class TestWarehouseLocation(unittest.TestCase):

    def test_full_label_and_same_place(self):
        addr = Address("St", "City", "DE", "111")
        loc1 = WarehouseLocation("W1", "Main", addr)
        loc2 = WarehouseLocation("W1", "Other", addr)
        loc3 = WarehouseLocation("W2", "Main", addr)
        self.assertEqual(loc1.full_label(), "W1 - Main")
        self.assertTrue(loc1.same_place(loc2))
        self.assertFalse(loc1.same_place(loc3))


class TestStockItem(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "US Dollar")
        book = Book(
            id=BookId("b1"),
            title="Book",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd),
        )
        addr = Address("St", "City", "DE", "111")
        loc = WarehouseLocation("W1", "Main", addr)
        self.item = StockItem(book, 10, loc)

    def test_increase(self):
        self.item.increase(5)
        self.assertEqual(self.item.quantity, 15)

    def test_decrease(self):
        self.item.decrease(3)
        self.assertEqual(self.item.quantity, 7)

    def test_decrease_too_much(self):
        with self.assertRaises(OutOfStockError):
            self.item.decrease(100)

    def test_is_empty(self):
        item = StockItem(self.item.book, 0, self.item.location)
        self.assertTrue(item.is_empty())
        self.assertFalse(self.item.is_empty())


class TestInventory(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "US Dollar")
        self.book = Book(
            id=BookId("b1"),
            title="Book",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd),
        )
        self.addr = Address("St", "City", "DE", "111")
        self.loc = WarehouseLocation("W1", "Main", self.addr)
        self.inv = Inventory()

    def test_add_book_first_time(self):
        self.inv.add_book(self.book, self.loc, 5)
        self.assertEqual(self.inv.available_quantity(self.book.isbn), 5)

    def test_add_book_existing_accumulates(self):
        self.inv.add_book(self.book, self.loc, 5)
        self.inv.add_book(self.book, self.loc, 3)
        self.assertEqual(self.inv.available_quantity(self.book.isbn), 8)

    def test_reserve_book(self):
        self.inv.add_book(self.book, self.loc, 5)
        self.inv.reserve_book(self.book.isbn, 3)
        self.assertEqual(self.inv.available_quantity(self.book.isbn), 2)

    def test_reserve_book_not_found(self):
        with self.assertRaises(BookNotFoundError):
            self.inv.reserve_book(ISBN("9780306406157"), 1)

    def test_has_book(self):
        self.assertFalse(self.inv.has_book(self.book.isbn))
        self.inv.add_book(self.book, self.loc, 1)
        self.assertTrue(self.inv.has_book(self.book.isbn))


class TestWarehouse(unittest.TestCase):

    def test_add_aisle_and_totals(self):
        addr = Address("St", "City", "DE", "111")
        loc = WarehouseLocation("W1", "Main", addr)
        warehouse = Warehouse("W1", "Main WH", loc)

        self.assertEqual(warehouse.total_titles(), 0)
        self.assertEqual(warehouse.total_stock(), 0)

        # add inventory
        usd = Currency("USD", "$", "US Dollar")
        book = Book(
            id=BookId("b1"),
            title="BookA",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd),
        )
        warehouse.inventory.add_book(book, loc, 5)

        self.assertEqual(warehouse.total_titles(), 1)
        self.assertEqual(warehouse.total_stock(), 5)

        # aisles
        aisle = Aisle("1", "Main aisle")
        warehouse.add_aisle(aisle)
        self.assertEqual(len(warehouse.aisles), 1)
class TestCustomerId(unittest.TestCase):

    def test_new_generates_unique(self):
        c1 = CustomerId.new()
        c2 = CustomerId.new()
        self.assertNotEqual(c1.value, c2.value)

    def test_short(self):
        c = CustomerId("abcd-efg-hij")
        self.assertEqual(c.short(), "abcd")


class TestPasswordHash(unittest.TestCase):

    def test_verify_correct(self):
        h = PasswordHash.from_plain("secret")
        self.assertTrue(h.verify("secret"))

    def test_verify_wrong(self):
        h = PasswordHash.from_plain("secret")
        self.assertFalse(h.verify("badpass"))

    def test_change_password_success(self):
        h = PasswordHash.from_plain("old")
        h2 = h.change_password("old", "newpass")
        self.assertTrue(h2.verify("newpass"))

    def test_change_password_invalid_old(self):
        h = PasswordHash.from_plain("old")
        with self.assertRaises(InvalidPasswordError):
            h.change_password("WRONG", "newpass")


class TestLoyaltyTier(unittest.TestCase):

    def test_qualifies(self):
        tier = LoyaltyTier("Gold", 10, required_points=100)
        self.assertTrue(tier.qualifies(200))
        self.assertFalse(tier.qualifies(50))

    def test_better_than(self):
        t1 = LoyaltyTier("Silver", 5, 50)
        t2 = LoyaltyTier("Gold", 10, 100)
        self.assertTrue(t2.better_than(t1))
        self.assertFalse(t1.better_than(t2))


class TestLoyaltyAccount(unittest.TestCase):

    def setUp(self):
        self.cid = CustomerId("c1")
        self.loyalty = LoyaltyAccount(self.cid, points=0)

    def test_add_points(self):
        self.loyalty.add_points(10)
        self.assertEqual(self.loyalty.points, 10)

    def test_add_negative_raises(self):
        with self.assertRaises(LoyaltyPointsError):
            self.loyalty.add_points(-5)

    def test_apply_tier(self):
        tiers = [
            LoyaltyTier("Bronze", 1, 0),
            LoyaltyTier("Silver", 5, 50),
            LoyaltyTier("Gold", 10, 100),
        ]
        self.loyalty.add_points(60)
        self.loyalty.apply_tier(tiers)
        self.assertEqual(self.loyalty.tier.name, "Silver")

    def test_current_discount(self):
        tier = LoyaltyTier("VIP", 15, 0)
        self.loyalty.tier = tier
        self.assertEqual(self.loyalty.current_discount(), 15.0)


class TestCustomerAccount(unittest.TestCase):

    def setUp(self):
        self.cid = CustomerId("c1")
        self.email = Email("user@example.com")
        self.addr = Address("St", "City", "DE", "111")
        self.name = PersonName("John", "Doe")
        self.password = PasswordHash.from_plain("pass")
        self.loyalty = LoyaltyAccount(self.cid)
        self.acc = CustomerAccount(
            id=self.cid,
            name=self.name,
            email=self.email,
            address=self.addr,
            password_hash=self.password,
            loyalty=self.loyalty
        )

    def test_check_password_success(self):
        self.acc.check_password("pass")  # если ошибки нет — тест прошёл

    def test_check_password_failure(self):
        with self.assertRaises(InvalidPasswordError):
            self.acc.check_password("wrong")

    def test_change_email_success(self):
        new_email = Email("new@example.com")
        self.acc.change_email(new_email)
        self.assertEqual(self.acc.email, new_email)

    def test_change_email_invalid(self):
        bad = Email("invalid")
        with self.assertRaises(ValueError):
            self.acc.change_email(bad)

    def test_add_loyalty_points_for_order(self):
        usd = Currency("USD", "$", "US Dollar")
        self.acc.add_loyalty_points_for_order(Money(25.7, usd))
        self.assertEqual(self.acc.loyalty.points, 25)  # int(amount)


class TestCartItem(unittest.TestCase):

    def test_line_total(self):
        usd = Currency("USD", "$", "US Dollar")
        book = Book(
            id=BookId("b1"),
            title="Book",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd)
        )
        item = CartItem(book, 3)
        total = item.line_total()
        self.assertEqual(total.amount, 30)

    def test_increase(self):
        item = CartItem(None, 2)
        item.increase(3)
        self.assertEqual(item.quantity, 5)


class TestShoppingCart(unittest.TestCase):

    def setUp(self):
        self.cid = CustomerId("c1")
        self.cart = ShoppingCart(self.cid)
        self.usd = Currency("USD", "$", "US Dollar")
        self.book = Book(
            id=BookId("b1"),
            title="Book",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, self.usd),
        )

    def test_add_item_new(self):
        self.cart.add_item(self.book, 2)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items[0].quantity, 2)

    def test_add_item_existing(self):
        self.cart.add_item(self.book, 1)
        self.cart.add_item(self.book, 3)
        self.assertEqual(self.cart.items[0].quantity, 4)

    def test_total_empty(self):
        total = self.cart.total()
        self.assertEqual(total.amount, 0)

    def test_total_non_empty(self):
        self.cart.add_item(self.book, 2)
        total = self.cart.total()
        self.assertEqual(total.amount, 20)

    def test_clear(self):
        self.cart.add_item(self.book, 1)
        self.cart.clear()
        self.assertEqual(len(self.cart.items), 0)


class TestOrderId(unittest.TestCase):

    def test_new_unique(self):
        o1 = OrderId.new()
        o2 = OrderId.new()
        self.assertNotEqual(o1.value, o2.value)

    def test_short(self):
        o = OrderId("abcd-xyz")
        self.assertEqual(o.short(), "abcd")


class TestOrderLine(unittest.TestCase):

    def test_line_total(self):
        usd = Currency("USD", "$", "US Dollar")
        line = OrderLine(
            book=None,
            quantity=4,
            unit_price=Money(5, usd),
        )
        self.assertEqual(line.line_total().amount, 20)

    def test_describe(self):
        usd = Currency("USD", "$", "US Dollar")
        book = Book(
            id=BookId("b1"),
            title="Test Book",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd)
        )
        line = OrderLine(book, 2, Money(10, usd))
        self.assertEqual(line.describe(), "Test Book x2")


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.usd = Currency("USD", "$", "US Dollar")
        self.customer = CustomerAccount(
            id=CustomerId("c1"),
            name=PersonName("John", "Doe"),
            email=Email("x@x.com"),
            address=Address("S", "C", "DE", "123"),
            password_hash=PasswordHash.from_plain("pass"),
            loyalty=LoyaltyAccount(CustomerId("c1"))
        )
        self.line1 = OrderLine(
            book=None,
            quantity=2,
            unit_price=Money(10, self.usd)
        )
        self.line2 = OrderLine(
            book=None,
            quantity=3,
            unit_price=Money(5, self.usd)
        )
        self.order = Order(
            id=OrderId("o1"),
            customer=self.customer,
            lines=[self.line1, self.line2],
            created_at=datetime.utcnow()
        )

    def test_total(self):
        total = self.order.total()
        self.assertEqual(total.amount, 2*10 + 3*5)

    def test_mark_paid_success(self):
        self.order.mark_paid()
        self.assertEqual(self.order.status, "PAID")

    def test_mark_paid_wrong_state(self):
        self.order.status = "CANCELLED"
        with self.assertRaises(OrderStateError):
            self.order.mark_paid()

    def test_cancel_success(self):
        self.order.cancel()
        self.assertEqual(self.order.status, "CANCELLED")

    def test_cancel_paid_raises(self):
        self.order.status = "PAID"
        with self.assertRaises(OrderStateError):
            self.order.cancel()

    def test_is_open(self):
        self.assertTrue(self.order.is_open())
        self.order.status = "CANCELLED"
        self.assertFalse(self.order.is_open())
class TestPaymentCard(unittest.TestCase):

    def setUp(self):
        self.usd = Currency("USD", "$", "US Dollar")
        self.card = PaymentCard(
            card_number="1111",
            holder_name=PersonName("John", "Doe"),
            expiry_month=12,
            expiry_year=2099,
            balance=Money(100, self.usd)
        )

    def test_is_valid_true(self):
        self.assertTrue(self.card.is_valid(date(2025, 1, 1)))

    def test_is_valid_false(self):
        expired = PaymentCard(
            "2222", PersonName("A", "B"),
            expiry_month=1, expiry_year=2000,
            balance=Money(100, self.usd)
        )
        self.assertFalse(expired.is_valid(date(2025, 1, 1)))

    def test_charge_success(self):
        self.card.charge(Money(40, self.usd), date.today())
        self.assertEqual(self.card.balance.amount, 60)

    def test_charge_expired_raises(self):
        old = PaymentCard(
            "3333", PersonName("A", "B"),
            expiry_month=1, expiry_year=2000,
            balance=Money(50, self.usd)
        )
        with self.assertRaises(PaymentDeclinedError):
            old.charge(Money(10, self.usd), date.today())

    def test_credit(self):
        self.card.credit(Money(25, self.usd))
        self.assertEqual(self.card.balance.amount, 125)


class TestPaymentTransaction(unittest.TestCase):

    def setUp(self):
        self.usd = Currency("USD", "$", "US Dollar")

        self.card_from = PaymentCard(
            "1111", PersonName("John", "Doe"),
            12, 2099, Money(100, self.usd)
        )
        self.card_to = PaymentCard(
            "2222", PersonName("Alice", "Smith"),
            12, 2099, Money(50, self.usd)
        )

        self.tx = PaymentTransaction(
            id="tx1",
            from_card=self.card_from,
            to_card=self.card_to,
            amount=Money(30, self.usd),
            created_at=datetime.utcnow()
        )

    def test_complete_success(self):
        self.tx.complete()
        self.assertEqual(self.tx.status, "COMPLETED")
        self.assertEqual(self.card_from.balance.amount, 70)  # 100 - 30
        self.assertEqual(self.card_to.balance.amount, 80)     # 50 + 30

    def test_complete_twice_raises(self):
        self.tx.complete()
        with self.assertRaises(PaymentDeclinedError):
            self.tx.complete()

    def test_fail(self):
        self.tx.fail("No funds")
        self.assertEqual(self.tx.status, "FAILED: No funds")

    def test_is_successful(self):
        self.assertFalse(self.tx.is_successful())
        self.tx.complete()
        self.assertTrue(self.tx.is_successful())


class TestPaymentGateway(unittest.TestCase):

    def setUp(self):
        self.gateway = PaymentGateway("PaySys")
        self.usd = Currency("USD", "$", "US Dollar")

        self.card1 = PaymentCard("1111", PersonName("J", "D"), 12, 2099, Money(100, self.usd))
        self.card2 = PaymentCard("2222", PersonName("A", "S"), 12, 2099, Money(50, self.usd))

    def test_transfer(self):
        tx = self.gateway.transfer(self.card1, self.card2, Money(20, self.usd))
        self.assertEqual(tx.status, "COMPLETED")
        self.assertEqual(self.card1.balance.amount, 80)
        self.assertEqual(self.card2.balance.amount, 70)

    def test_refund(self):
        tx = self.gateway.refund(self.card1, self.card2, Money(30, self.usd))
        # refund reverses direction: card2 → card1
        self.assertEqual(self.card2.balance.amount, 20)  # 50 - 30
        self.assertEqual(self.card1.balance.amount, 130) # 100 + 30
        self.assertEqual(tx.status, "COMPLETED")


class TestInvoice(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "US Dollar")
        customer = CustomerAccount(
            id=CustomerId("c1"),
            name=PersonName("John", "Doe"),
            email=Email("x@x.com"),
            address=Address("St", "City", "DE", "111"),
            password_hash=PasswordHash.from_plain("123"),
            loyalty=LoyaltyAccount(CustomerId("c1"))
        )
        line = OrderLine(None, 1, Money(100, usd))
        self.order = Order(
            id=OrderId("o1"),
            customer=customer,
            lines=[line],
            created_at=datetime.utcnow()
        )
        self.invoice = Invoice(
            id="inv1",
            order=self.order,
            issued_at=datetime.utcnow(),
            total=Money(100, usd)
        )

    def test_mark_paid(self):
        self.invoice.mark_paid()
        self.assertEqual(self.order.status, "PAID")

    def test_is_overdue_true(self):
        old_date = date.today().replace(year=date.today().year - 1)
        self.assertTrue(self.invoice.is_overdue(old_date))

    def test_is_overdue_false_if_paid(self):
        self.order.status = "PAID"
        old_date = date.today().replace(year=date.today().year - 1)
        self.assertFalse(self.invoice.is_overdue(old_date))


class TestDiscountCode(unittest.TestCase):

    def test_apply_active(self):
        usd = Currency("USD", "$", "US Dollar")
        dc = DiscountCode("SALE10", 10)
        new = dc.apply(Money(100, usd))
        self.assertEqual(new.amount, 90)

    def test_apply_inactive(self):
        usd = Currency("USD", "$", "US Dollar")
        dc = DiscountCode("SALE10", 10, active=False)
        new = dc.apply(Money(100, usd))
        self.assertEqual(new.amount, 100)

    def test_deactivate(self):
        dc = DiscountCode("X", 5)
        dc.deactivate()
        self.assertFalse(dc.active)


class TestDeliveryMethod(unittest.TestCase):

    def test_is_free(self):
        usd = Currency("USD", "$", "US Dollar")
        free = DeliveryMethod("F", "Free", Money(0, usd))
        paid = DeliveryMethod("P", "Paid", Money(10, usd))
        self.assertTrue(free.is_free())
        self.assertFalse(paid.is_free())

    def test_label(self):
        usd = Currency("USD", "$", "US Dollar")
        dm = DeliveryMethod("P", "Courier", Money(10, usd))
        self.assertEqual(dm.label(), "Courier ($10)")


class TestShipmentTracking(unittest.TestCase):

    def test_add_event_and_last_event(self):
        tr = ShipmentTracking("T1", "Init")
        tr.add_event("Packed")
        tr.add_event("Shipped")
        self.assertEqual(tr.last_event(), "Shipped")
        self.assertIn("Packed", tr.history)


class TestShipment(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "US Dollar")
        customer = CustomerAccount(
            id=CustomerId("c1"),
            name=PersonName("J", "D"),
            email=Email("x@x.com"),
            address=Address("St", "C", "DE", "123"),
            password_hash=PasswordHash.from_plain("p"),
            loyalty=LoyaltyAccount(CustomerId("c1"))
        )
        line = OrderLine(None, 1, Money(10, usd))
        order = Order(OrderId("o1"), customer, [line], datetime.utcnow())
        method = DeliveryMethod("COU", "Courier", Money(10, usd))
        tracking = ShipmentTracking("T1", "Init")

        self.shipment = Shipment("S1", order, method, tracking)

    def test_ship(self):
        self.shipment.ship()
        self.assertTrue(self.shipment.is_shipped())
        self.assertEqual(self.shipment.tracking.last_event(), "Shipped")


class TestReservation(unittest.TestCase):

    def setUp(self):
        usd = Currency("USD", "$", "US Dollar")
        book = Book(
            id=BookId("b1"),
            title="Book",
            author=Author("A1", PersonName("John", "Doe")),
            publisher=Publisher("P1", "Pub"),
            isbn=ISBN("9780306406157"),
            base_price=Money(10, usd),
        )
        customer = CustomerAccount(
            id=CustomerId("c1"),
            name=PersonName("J", "D"),
            email=Email("x@x.com"),
            address=Address("St", "C", "DE", "123"),
            password_hash=PasswordHash.from_plain("p"),
            loyalty=LoyaltyAccount(CustomerId("c1"))
        )
        self.res = Reservation(
            id="r1",
            book=book,
            customer=customer,
            expires_at=datetime.utcnow(),
        )

    def test_expire(self):
        self.res.expire()
        self.assertFalse(self.res.is_active())

    def test_is_active_false_after_expiry_time(self):
        old_time = datetime.utcnow().replace(year=datetime.utcnow().year - 1)
        self.res.expires_at = old_time
        self.assertFalse(self.res.is_active())


class TestSupplier(unittest.TestCase):

    def test_contact_and_labeled(self):
        s = Supplier("S1", "BookSup", Email("sup@example.com"))
        msg = s.contact("Hello")
        self.assertIn("Email sent to sup@example.com", msg)
        self.assertEqual(s.labeled(), "BookSup <sup@example.com>")

if __name__ == "__main__":
    unittest.main()
