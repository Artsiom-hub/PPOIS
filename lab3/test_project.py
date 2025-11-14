import unittest
import hashlib
import datetime
from travel import *
# ==== импортируем тестируемый код ====

from dataclasses import dataclass, field

class TestUser(unittest.TestCase):

    def setUp(self):
        self.raw_password = "secret123"
        self.hashed = hashlib.sha256(self.raw_password.encode()).hexdigest()
        self.user = User(
            user_id="u1",
            email="test@example.com",
            password_hash=self.hashed
        )

    def test_password_correct(self):
        self.assertTrue(self.user.check_password("secret123"))

    def test_password_incorrect(self):
        self.assertFalse(self.user.check_password("wrongpass"))

    def test_user_deactivate(self):
        self.user.deactivate()
        self.assertFalse(self.user.active)


# ============================================================
#                       CUSTOMER TESTS
# ============================================================

class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.customer = Customer(
            user_id="c1",
            email="cust@example.com",
            password_hash="hash",
            full_name="John Doe"
        )

    def test_add_card(self):
        acc = BankAccount("IB1", "John Doe", 500)
        card = PaymentCard(
            card_number="1234",
            owner=self.customer,
            bank_account=acc,
            cvv="123",
            expiry_month=12,
            expiry_year=2050
        )
        self.customer.add_card(card)
        self.assertEqual(self.customer.cards[0], card)

    def test_get_default_card_no_cards(self):
        with self.assertRaises(CardNotFoundError):
            self.customer.get_default_card()


# ============================================================
#                      TRAVEL AGENT TESTS
# ============================================================

class DummyBooking:
    def __init__(self, price):
        self.total_price = price


class TestTravelAgent(unittest.TestCase):

    def setUp(self):
        self.agent = TravelAgent(
            user_id="a1",
            email="agent@example.com",
            password_hash="hash",
            agency_name="BestTravel",
            commission_rate=0.1
        )

    def test_register_booking(self):
        booking = DummyBooking(100)
        self.agent.register_booking(booking)
        self.assertEqual(self.agent.managed_bookings[0], booking)

    def test_calculate_commission(self):
        booking = DummyBooking(200)
        self.assertEqual(self.agent.calculate_commission(booking), 20.0)


# ============================================================
#                     BANK ACCOUNT TESTS
# ============================================================

class TestBankAccount(unittest.TestCase):

    def setUp(self):
        self.acc = BankAccount("IBAN1", "Owner", 100)

    def test_deposit(self):
        self.acc.deposit(50)
        self.assertEqual(self.acc.balance, 150)

    def test_deposit_negative(self):
        with self.assertRaises(ValueError):
            self.acc.deposit(-10)

    def test_withdraw_ok(self):
        self.acc.withdraw(40)
        self.assertEqual(self.acc.balance, 60)

    def test_withdraw_insufficient(self):
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(200)


# ============================================================
#                     PAYMENT CARD TESTS
# ============================================================

class TestPaymentCard(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.acc = BankAccount("IB1", "Test", 300)
        self.card = PaymentCard(
            card_number="1234",
            owner=self.customer,
            bank_account=self.acc,
            cvv="111",
            expiry_month=12,
            expiry_year=datetime.date.today().year + 1
        )

    def test_card_valid(self):
        self.assertTrue(self.card.is_valid())

    def test_card_expired(self):
        expired = PaymentCard(
            card_number="1111",
            owner=self.customer,
            bank_account=self.acc,
            cvv="222",
            expiry_month=1,
            expiry_year=2000
        )
        self.assertFalse(expired.is_valid())

    def test_charge_success(self):
        self.card.charge(100)
        self.assertEqual(self.acc.balance, 200)

    def test_charge_expired(self):
        expired = PaymentCard(
            card_number="1111",
            owner=self.customer,
            bank_account=self.acc,
            cvv="111",
            expiry_month=1,
            expiry_year=2000
        )
        with self.assertRaises(PaymentDeclinedError):
            expired.charge(50)

    def test_refund(self):
        self.card.refund(50)
        self.assertEqual(self.acc.balance, 350)


# ============================================================
#                   PAYMENT GATEWAY TESTS
# ============================================================

class TestPaymentGateway(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.acc1 = BankAccount("IB1", "owner1", 200)
        self.acc2 = BankAccount("IB2", "owner2", 100)

        self.card1 = PaymentCard("111", self.customer, self.acc1, "111", 12, 2050)
        self.card2 = PaymentCard("222", self.customer, self.acc2, "222", 12, 2050)

        self.gateway = PaymentGateway("GATE")

    def test_successful_transfer(self):
        tx = self.gateway.transfer(self.card1, self.card2, 50)
        self.assertEqual(tx.status, "SUCCESS")
        self.assertEqual(self.acc1.balance, 150)
        self.assertEqual(self.acc2.balance, 150)

    def test_transfer_insufficient_funds(self):
        with self.assertRaises(InsufficientFundsError):
            self.gateway.transfer(self.card1, self.card2, 500)

        # убедимся, что транзакция зафиксирована как FAILED
        last_tx = list(self.gateway.transactions.values())[-1]
        self.assertEqual(last_tx.status, "FAILED")

    def test_get_transaction(self):
        tx = self.gateway.transfer(self.card1, self.card2, 10)
        fetched = self.gateway.get_transaction(tx.tx_id)
        self.assertEqual(fetched, tx)


# ============================================================
#                    GEO / DESTINATION TESTS
# ============================================================

class TestGeo(unittest.TestCase):

    def test_country_add_airport(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        airport = type("Airport", (), {"code": "BER"})()  # dummy airport
        country.add_airport(airport)
        self.assertEqual(country.airports[0].code, "BER")

    def test_find_airport(self):
        country = Country("ES", "Spain", "EUR")
        a1 = type("Airport", (), {"code": "MAD"})()
        a2 = type("Airport", (), {"code": "BCN"})()
        country.add_airport(a1)
        country.add_airport(a2)
        self.assertEqual(country.find_airport("BCN"), a2)

    def test_city_describe(self):
        country = Country("FR", "France", "EUR")
        city = City("Paris", country, population=2000000)
        self.assertEqual(
            city.describe(),
            "Paris, France. Population: 2000000"
        )

    def test_destination_tags(self):
        country = Country("JP", "Japan", "JPY")
        city = City("Tokyo", country)
        dest = Destination("TKY", city, "desc")

        dest.add_tag("food")
        dest.add_tag("anime")
        dest.add_tag("food")  # duplicate shouldn't appear twice

        self.assertTrue(dest.has_tag("food"))
        self.assertEqual(len(dest.tags), 2)
# ============================================================
#                     AIRPORT TESTS
# ============================================================

class TestAirport(unittest.TestCase):

    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        self.airport = Airport(
            code="BER",
            name="Berlin Brandenburg",
            city=city
        )

    def test_add_terminal(self):
        self.airport.add_terminal("T1")
        self.airport.add_terminal("T2")
        self.assertEqual(self.airport.terminals, ["T1", "T2"])

    def test_full_description(self):
        desc = self.airport.full_description()
        self.assertEqual(desc, "Berlin Brandenburg (BER), Berlin, DE")


# ============================================================
#                         SEAT TESTS
# ============================================================

class TestSeat(unittest.TestCase):

    def setUp(self):
        self.seat = Seat("12A", "Economy", True)

    def test_reserve_ok(self):
        self.seat.reserve()
        self.assertTrue(self.seat.is_occupied)

    def test_reserve_already_taken(self):
        self.seat.reserve()
        with self.assertRaises(SeatUnavailableError):
            self.seat.reserve()

    def test_free(self):
        self.seat.reserve()
        self.seat.free()
        self.assertFalse(self.seat.is_occupied)


# ============================================================
#                   PASSENGER PROFILE TESTS
# ============================================================

class TestPassengerProfile(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("c1", "x@y.z", "hash")
        self.profile = PassengerProfile(
            customer=self.customer,
            passport_number="X123",
            nationality="DE",
            date_of_birth=datetime.date(2000, 5, 10)
        )

    def test_add_baggage(self):
        bag = Baggage("B1", 10)
        self.profile.add_baggage(bag)
        self.assertEqual(self.profile.baggage[0], bag)

    def test_age(self):
        # проверяем возраст относительно сегодняшней даты
        today = datetime.date.today()
        expected_age = today.year - 2000 - (
            (today.month, today.day) < (5, 10)
        )
        self.assertEqual(self.profile.age(), expected_age)


# ============================================================
#                       BAGGAGE TESTS
# ============================================================

class TestBaggage(unittest.TestCase):

    def test_overweight_fee_none(self):
        bag = Baggage("T1", 15)
        self.assertEqual(bag.overweight_fee(limit=20, fee_per_kg=10), 0.0)

    def test_overweight_fee(self):
        bag = Baggage("T2", 25)
        # 25 - 20 = 5 kg overweight → 5 * 10
        self.assertEqual(bag.overweight_fee(limit=20, fee_per_kg=10), 50.0)


# ============================================================
#                         FLIGHT TESTS
# ============================================================

class TestFlight(unittest.TestCase):

    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        airport1 = Airport("BER", "Brandenburg", city)
        airport2 = Airport("MUC", "Munich Intl", City("Munich", country))

        dep = datetime.datetime(2030, 1, 1, 12, 0)
        arr = datetime.datetime(2030, 1, 1, 15, 0)

        self.flight = Flight(
            flight_number="LH123",
            origin=airport1,
            destination=airport2,
            departure_time=dep,
            arrival_time=arr,
            base_price=200.0
        )

    def test_add_seat(self):
        seat = Seat("10A", "Economy", True)
        self.flight.add_seat(seat)
        self.assertIn("10A", self.flight.seats)

    def test_reserve_seat_ok(self):
        seat = Seat("11B", "Economy", False)
        self.flight.add_seat(seat)
        reserved = self.flight.reserve_seat("11B")
        self.assertTrue(reserved.is_occupied)

    def test_reserve_seat_not_exists(self):
        with self.assertRaises(SeatUnavailableError):
            self.flight.reserve_seat("XX99")

    def test_available_seats_count(self):
        s1 = Seat("1A", "Economy", True)
        s2 = Seat("1B", "Economy", False)
        s3 = Seat("1C", "Economy", False)

        self.flight.add_seat(s1)
        self.flight.add_seat(s2)
        self.flight.add_seat(s3)

        s1.reserve()   # 1 занято, 2 свободно

        self.assertEqual(self.flight.available_seats_count(), 2)
# ============================================================
#                     ROOM TYPE TESTS
# ============================================================

class TestRoomType(unittest.TestCase):

    def setUp(self):
        self.rt = RoomType(code="STD", name="Standard", max_guests=2, base_price=100.0)

    def test_price_one_guest(self):
        self.assertEqual(self.rt.price_for_guests(1), 100.0)

    def test_price_two_guests(self):
        # второй гость +30%
        self.assertEqual(self.rt.price_for_guests(2), 100.0 + 100.0 * 0.3)

    def test_too_many_guests(self):
        with self.assertRaises(OverbookingError):
            self.rt.price_for_guests(3)


# ============================================================
#                       ROOM TESTS
# ============================================================

class TestRoom(unittest.TestCase):

    def setUp(self):
        rt = RoomType("STD", "Standard", 2, 100)
        self.room = Room(number="101", room_type=rt, floor=1)

    def test_occupy_ok(self):
        self.room.occupy()
        self.assertTrue(self.room.occupied)

    def test_occupy_already(self):
        self.room.occupy()
        with self.assertRaises(OverbookingError):
            self.room.occupy()

    def test_release(self):
        self.room.occupy()
        self.room.release()
        self.assertFalse(self.room.occupied)


# ============================================================
#                       HOTEL TESTS
# ============================================================

class TestHotel(unittest.TestCase):

    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        self.hotel = Hotel(name="Grand", city=city, address="Main St")

        self.rt_std = RoomType("STD", "Standard", 2, 100)
        self.rt_del_
# ============================================================
#                  LOYALTY ACCOUNT TESTS
# ============================================================

class TestLoyaltyAccount(unittest.TestCase):

    def setUp(self):
        cust = Customer("c1", "mail", "hash")
        self.program = LoyaltyProgram("LP", base_multiplier=1.5)
        self.program.add_level("SILVER", 300)
        self.program.add_level("GOLD", 1000)

        self.acc = LoyaltyAccount(customer=cust, program=self.program)

        # dummy booking
        self.booking = type("BookingStub", (), {"total_price": 200})()

    def test_add_points_for_booking(self):
        self.acc.add_points_for_booking(self.booking)
        # gained = 200 * 1.5 = 300
        self.assertEqual(self.acc.points, 300)
        self.assertEqual(self.acc.level, "SILVER")

    def test_add_points_reaches_gold(self):
        self.acc.points = 800
        self.acc.add_points_for_booking(self.booking)  # +300 => 1100
        self.assertEqual(self.acc.level, "GOLD")

    def test_redeem_points_ok(self):
        self.acc.points = 500
        self.acc.redeem_points(200)
        self.assertEqual(self.acc.points, 300)

    def test_redeem_points_insufficient(self):
        self.acc.points = 50
        with self.assertRaises(InsufficientFundsError):
            self.acc.redeem_points(100)


# ============================================================
#                        COUPON TESTS
# ============================================================

class TestCoupon(unittest.TestCase):

    def test_coupon_apply_ok(self):
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        c = Coupon("WELCOME", 10, expires)
        new_price = c.apply(200)
        self.assertEqual(new_price, 180)
        self.assertTrue(c.used)

    def test_coupon_expired(self):
        expires = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        c = Coupon("OLD", 10, expires)
        with self.assertRaises(CouponExpiredError):
            c.apply(200)

    def test_coupon_used_twice(self):
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        c = Coupon("ONEUSE", 10, expires)
        c.apply(200)
        with self.assertRaises(CouponExpiredError):
            c.apply(200)


# ============================================================
#                       DISCOUNT TESTS
# ============================================================

class TestDiscount(unittest.TestCase):

    def setUp(self):
        self.disc = Discount("BIGSALE", percent=20, min_amount=300)

    def test_discount_applies(self):
        self.assertEqual(self.disc.apply_if_applicable(300), 240.0)

    def test_discount_not_applied(self):
        self.assertEqual(self.disc.apply_if_applicable(299), 299)


# ============================================================
#                        CART ITEM TESTS
# ============================================================

class TestCartItem(unittest.TestCase):

    def test_line_total(self):
        item = CartItem("FLIGHT", None, price=100, quantity=3)
        self.assertEqual(item.line_total(), 300)

    def test_increase_qty(self):
        item = CartItem("FLIGHT", None, price=50, quantity=1)
        item.increase_qty()
        item.increase_qty(2)
        self.assertEqual(item.quantity, 4)


# ============================================================
#                           CART TESTS
# ============================================================

class TestCart(unittest.TestCase):

    def setUp(self):
        cust = Customer("c1", "mail", "hash")
        self.cart = Cart(customer=cust)

    def test_add_item(self):
        item = CartItem("HOTEL", None, 120)
        self.cart.add_item(item)
        self.assertIn(item, self.cart.items)

    def test_total(self):
        self.cart.add_item(CartItem("F1", None, 100, 2))  # 200
        self.cart.add_item(CartItem("F2", None, 50, 3))   # 150
        self.assertEqual(self.cart.total(), 350)

    def test_clear(self):
        self.cart.add_item(CartItem("X", None, 10))
        self.cart.clear()
        self.assertEqual(len(self.cart.items), 0)
# ============================================================
#                     SEARCH CRITERIA TESTS
# ============================================================

class TestSearchCriteria(unittest.TestCase):

    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        self.airport_ber = Airport("BER", "Brandenburg", city)
        self.airport_muc = Airport("MUC", "Munich", city)

    def test_validate_ok(self):
        sc = SearchCriteria(origin=self.airport_ber, destination=self.airport_muc)
        sc.validate()  # не должно бросать

    def test_validate_missing_origin(self):
        sc = SearchCriteria(origin=None, destination=self.airport_muc)
        with self.assertRaises(InvalidSearchCriteriaError):
            sc.validate()

    def test_validate_missing_destination(self):
        sc = SearchCriteria(origin=self.airport_ber, destination=None)
        with self.assertRaises(InvalidSearchCriteriaError):
            sc.validate()

    def test_validate_same_origin_destination(self):
        sc = SearchCriteria(origin=self.airport_ber, destination=self.airport_ber)
        with self.assertRaises(InvalidSearchCriteriaError):
            sc.validate()


# ============================================================
#                RECOMMENDATION ENGINE TESTS
# ============================================================

class TestRecommendationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RecommendationEngine()

        country = Country("JP", "Japan", "JPY")
        city_tokyo = City("Tokyo", country)
        city_osaka = City("Osaka", country)

        self.dest_tokyo = Destination("TOK", city_tokyo, "Tokyo desc", tags=["anime", "food"])
        self.dest_osaka = Destination("OSA", city_osaka, "Osaka desc", tags=["food", "street"])
        self.dest_empty = Destination("EM", city_tokyo, "Empty desc", tags=[])

        self.customer = Customer("cust1", "mail", "hash")

    def test_add_history(self):
        self.engine.add_history(self.customer, self.dest_tokyo)
        self.assertIn(self.dest_tokyo, self.engine.history["cust1"])

    def test_recommend_on_common_tags(self):
        # клиент видел Tokyo → tags = anime, food
        self.engine.add_history(self.customer, self.dest_tokyo)

        all_dest = [self.dest_tokyo, self.dest_osaka, self.dest_empty]

        result = self.engine.recommend(self.customer, all_dest)

        # Osaka имеет общий тег 'food', значит должна быть в списке
        self.assertIn(self.dest_osaka, result)
        # пустая не должна быть
        self.assertNotIn(self.dest_empty, result)

    def test_recommend_sorted_by_score(self):
        # Tokyo: tags = anime, food
        self.engine.add_history(self.customer, self.dest_tokyo)

        # osaka — 1 общий тег, empty — 0, tokyo — 2 общих тега с самим собой
        all_dest = [self.dest_osaka, self.dest_tokyo]

        result = self.engine.recommend(self.customer, all_dest)

        # Tokyo имеет больше совпадений → должна быть первой
        self.assertEqual(result[0], self.dest_tokyo)


# ============================================================
#                      NOTIFICATION TESTS
# ============================================================

class TestNotification(unittest.TestCase):

    def setUp(self):
        self.user = User("u1", "mail", "hash")
        self.n = Notification("n1", self.user, "Hello world notification message!")

    def test_mark_read(self):
        self.n.mark_read()
        self.assertTrue(self.n.read)

    def test_short(self):
        text = "a" * 60
        n2 = Notification("n2", self.user, text)
        self.assertEqual(n2.short(), text[:40])


# ============================================================
#                 EMAIL NOTIFICATION TESTS
# ============================================================

class TestEmailNotification(unittest.TestCase):

    def setUp(self):
        self.user = User("u1", "x@y.z", "hash")
        self.en = EmailNotification(
            notification_id="e1",
            user=self.user,
            message="Booking confirmed",
            subject="Your booking",
            email_address="x@y.z"
        )

    def test_format_email(self):
        formatted = self.en.format_email()
        self.assertIn("To: x@y.z", formatted)
        self.assertIn("Subject: Your booking", formatted)
        self.assertIn("Booking confirmed", formatted)


# ============================================================
#                  SMS NOTIFICATION TESTS
# ============================================================

class TestSMSNotification(unittest.TestCase):

    def setUp(self):
        self.user = User("u1", "mail", "hash")
        self.sms = SMSNotification(
            notification_id="s1",
            user=self.user,
            message="Your code is 1234",
            phone_number="+4912345678"
        )

    def test_format_sms(self):
        txt = self.sms.format_sms()
        self.assertEqual(txt, "SMS to +4912345678: Your code is 1234")
# ============================================================
#                     CHAT MESSAGE TESTS
# ============================================================

class TestChatMessage(unittest.TestCase):

    def setUp(self):
        self.user = User("u1", "u@mail", "hash")
        self.msg = ChatMessage(
            message_id="m1",
            author=self.user,
            text="Hello, this is a long message used for preview testing!"
        )

    def test_preview(self):
        self.assertEqual(
            self.msg.preview(),
            "Hello, this is a long message used for previ"
        )


# ============================================================
#                     SUPPORT TICKET TESTS
# ============================================================

class TestSupportTicket(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("c1", "c@mail", "hash")
        self.ticket = SupportTicket(
            ticket_id="t1",
            customer=self.customer,
            subject="Issue with booking"
        )

    def test_add_message(self):
        msg = ChatMessage("m1", self.customer, "Help pls")
        self.ticket.add_message(msg)
        self.assertIn(msg, self.ticket.messages)

    def test_close(self):
        self.ticket.close()
        self.assertEqual(self.ticket.status, "CLOSED")


# ============================================================
#                           SESSION TESTS
# ============================================================

class TestSession(unittest.TestCase):

    def setUp(self):
        self.user = User("u1", "u@mail", "hash")
        self.session = Session(session_id="s1", user=self.user)

    def test_is_active(self):
        self.assertTrue(self.session.is_active())

    def test_extend(self):
        old_exp = self.session.expires_at
        self.session.extend(3)
        self.assertEqual(self.session.expires_at, old_exp + datetime.timedelta(hours=3))


# ============================================================
#                  AUTHENTICATION SERVICE TESTS
# ============================================================

class TestAuthenticationService(unittest.TestCase):

    def setUp(self):
        self.auth = AuthenticationService()
        raw_pass = "secret"
        hashed = AuthenticationService.hash_password(raw_pass)
        self.user = User("u1", "mail", hashed)
        self.raw_pass = raw_pass

    def test_hash_password(self):
        self.assertEqual(
            AuthenticationService.hash_password("abc"),
            hashlib.sha256("abc".encode()).hexdigest()
        )

    def test_authenticate_success(self):
        session = self.auth.authenticate(self.user, self.raw_pass)
        self.assertIsInstance(session, Session)
        self.assertIn(session.session_id, self.auth.sessions)

    def test_authenticate_fail(self):
        with self.assertRaises(InvalidPasswordError):
            self.auth.authenticate(self.user, "wrongpass")

    def test_get_session_ok(self):
        session = self.auth.authenticate(self.user, self.raw_pass)
        fetched = self.auth.get_session(session.session_id)
        self.assertEqual(fetched, session)

    def test_get_session_expired(self):
        session = self.auth.authenticate(self.user, self.raw_pass)

        # вручную истекаем срок действия
        session.expires_at = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)

        with self.assertRaises(AuthenticationError):
            self.auth.get_session(session.session_id)


if __name__ == "__main__":
    unittest.main()
