import unittest
import datetime

from core.geography.locations import Country, City
from core.geography.airports import Airport

from core.flights.seats import Seat
from core.flights.flights import Flight
from core.flights.passengers import PassengerProfile, Baggage
from core.users.models import Customer


class TestSeat(unittest.TestCase):
    def test_seat_reserve(self):
        s = Seat("1A", "Economy", True)
        s.reserve()
        self.assertTrue(s.is_occupied)

    def test_seat_double(self):
        s = Seat("1A", "Economy", True)
        s.reserve()
        with self.assertRaises(Exception):
            s.reserve()

    def test_seat_free(self):
        s = Seat("2B", "Economy", False)
        s.reserve()
        s.free()
        self.assertFalse(s.is_occupied)


class TestPassengerProfile(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "mail", "hash", full_name="John Doe")
        self.profile = PassengerProfile(
            customer=self.customer,
            passport_number="P123",
            nationality="USA",
            date_of_birth=datetime.date(2000, 1, 1)
        )

    def test_add_baggage(self):
        bag = Baggage("BG1", 15)
        self.profile.add_baggage(bag)
        self.assertEqual(len(self.profile.baggage), 1)

    def test_age(self):
        self.assertEqual(self.profile.age(), datetime.date.today().year - 2000)


class TestFlight(unittest.TestCase):
    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        origin = Airport("BER", "Berlin", city)
        dest = Airport("MUC", "Munich", city)

        self.flight = Flight(
            flight_number="LH100",
            origin=origin,
            destination=dest,
            departure_time=datetime.datetime.now(),
            arrival_time=datetime.datetime.now() + datetime.timedelta(hours=1),
            base_price=150.0
        )

    def test_add_seat(self):
        seat = Seat("1A", "Economy", True)
        self.flight.add_seat(seat)
        self.assertIn("1A", self.flight.seats)

    def test_reserve_seat(self):
        seat = Seat("2B", "Economy", False)
        self.flight.add_seat(seat)
        result = self.flight.reserve_seat("2B")
        self.assertTrue(result.is_occupied)

    def test_reserve_nonexistent_seat(self):
        with self.assertRaises(Exception):
            self.flight.reserve_seat("XX")
