import unittest
import datetime
import uuid

from core.bookings.base import Booking
from core.bookings.flight_booking import FlightBooking
from core.bookings.hotel_booking import HotelBooking

from core.users.models import Customer
from core.flights.flights import Flight
from core.flights.seats import Seat
from core.flights.passengers import PassengerProfile
from core.hotels.hotels import Hotel
from core.hotels.rooms import Room, RoomType
from core.geography.locations import Country, City
from core.geography.airports import Airport


class TestBookingBase(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.b = Booking(
            booking_id="b1",
            customer=self.customer,
            created_at=datetime.datetime.utcnow(),
            total_price=100.0
        )

    def test_confirm(self):
        self.b.confirm()
        self.assertEqual(self.b.status, "CONFIRMED")

    def test_cancel(self):
        self.b.cancel()
        self.assertEqual(self.b.status, "CANCELLED")


class TestFlightBooking(unittest.TestCase):
    def setUp(self):
        customer = Customer("c1", "mail", "hash")
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        airport = Airport("BER", "Berlin", city)

        self.flight = Flight(
            "LH100",
            airport,
            airport,
            datetime.datetime.utcnow(),
            datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            200.0
        )
        seat = Seat("1A", "Economy", True)
        self.flight.add_seat(seat)

        passenger = PassengerProfile(customer, "P123", "DEU", datetime.date(2000, 1, 1))

        self.booking = FlightBooking(
            booking_id="fb1",
            customer=customer,
            created_at=datetime.datetime.utcnow(),
            total_price=200.0,
            flight=self.flight,
            passenger=passenger
        )

    def test_assign_seat(self):
        seat = self.flight.reserve_seat("1A")
        self.booking.assign_seat(seat)
        self.assertEqual(self.booking.seat.seat_number, "1A")

    def test_add_baggage_fee(self):
        self.booking.add_baggage_fee(50)
        self.assertEqual(self.booking.baggage_fees, 50)
        self.assertEqual(self.booking.total_price, 250)


class TestHotelBooking(unittest.TestCase):
    def test_nights(self):
        customer = Customer("c1", "mail", "hash")
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        hotel = Hotel("Test Hotel", city)
        rt = RoomType("Standard", 2, [])
        room = Room("101", rt, 120)
        hotel.add_room(room)

        today = datetime.date.today()
        hb = HotelBooking(
            booking_id="hb1",
            customer=customer,
            created_at=datetime.datetime.utcnow(),
            total_price=120,
            hotel=hotel,
            room=room,
            check_in=today,
            check_out=today + datetime.timedelta(days=3)
        )

        self.assertEqual(hb.nights(), 3)
import unittest
import datetime
import uuid

from core.bookings.base import Booking
from core.bookings.flight_booking import FlightBooking
from core.bookings.hotel_booking import HotelBooking

from core.users.models import Customer
from core.flights.flights import Flight
from core.flights.seats import Seat
from core.flights.passengers import PassengerProfile
from core.hotels.hotels import Hotel
from core.hotels.rooms import Room, RoomType
from core.geography.locations import Country, City
from core.geography.airports import Airport


class TestBookingBase(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("c1", "mail", "hash")
        self.b = Booking(
            booking_id="b1",
            customer=self.customer,
            created_at=datetime.datetime.utcnow(),
            total_price=100.0
        )

    def test_confirm(self):
        self.b.confirm()
        self.assertEqual(self.b.status, "CONFIRMED")

    def test_cancel(self):
        self.b.cancel()
        self.assertEqual(self.b.status, "CANCELLED")


class TestFlightBooking(unittest.TestCase):
    def setUp(self):
        customer = Customer("c1", "mail", "hash")
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        airport = Airport("BER", "Berlin", city)

        self.flight = Flight(
            "LH100",
            airport,
            airport,
            datetime.datetime.utcnow(),
            datetime.datetime.utcnow() + datetime.timedelta(hours=2),
            200.0
        )
        seat = Seat("1A", "Economy", True)
        self.flight.add_seat(seat)

        passenger = PassengerProfile(customer, "P123", "DEU", datetime.date(2000, 1, 1))

        self.booking = FlightBooking(
            booking_id="fb1",
            customer=customer,
            created_at=datetime.datetime.utcnow(),
            total_price=200.0,
            flight=self.flight,
            passenger=passenger
        )

    def test_assign_seat(self):
        seat = self.flight.reserve_seat("1A")
        self.booking.assign_seat(seat)
        self.assertEqual(self.booking.seat.seat_number, "1A")

    def test_add_baggage_fee(self):
        self.booking.add_baggage_fee(50)
        self.assertEqual(self.booking.baggage_fees, 50)
        self.assertEqual(self.booking.total_price, 250)


class TestHotelBooking(unittest.TestCase):
    def test_nights(self):
        customer = Customer("c1", "mail", "hash")
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        hotel = Hotel("Test Hotel", city)
        rt = RoomType("Standard", 2, [])
        room = Room("101", rt, 120)
        hotel.add_room(room)

        today = datetime.date.today()
        hb = HotelBooking(
            booking_id="hb1",
            customer=customer,
            created_at=datetime.datetime.utcnow(),
            total_price=120,
            hotel=hotel,
            room=room,
            check_in=today,
            check_out=today + datetime.timedelta(days=3)
        )

        self.assertEqual(hb.nights(), 3)
