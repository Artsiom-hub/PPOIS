import unittest

from core.hotels.hotels import Hotel
from core.hotels.rooms import Room, RoomType
from core.geography.locations import Country, City


class TestRoom(unittest.TestCase):
    def setUp(self):
        self.rt = RoomType("Standard", 2, ["WiFi"])
        self.room = Room("101", self.rt, 100)

    def test_room_reserve(self):
        self.room.reserve()
        self.assertFalse(self.room.is_available)

    def test_room_release(self):
        self.room.reserve()
        self.room.release()
        self.assertTrue(self.room.is_available)


class TestHotel(unittest.TestCase):
    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        self.hotel = Hotel("Test Hotel", city)
        rt = RoomType("Standard", 2, ["WiFi"])
        self.room = Room("101", rt, 120)
        self.hotel.add_room(self.room)

    def test_add_room(self):
        self.assertEqual(len(self.hotel.rooms), 1)

    def test_find_available_room(self):
        found = self.hotel.find_available_room(self.room.room_type)
        self.assertEqual(found, self.room)

    def test_available_rooms_count(self):
        self.assertEqual(self.hotel.available_rooms_count(), 1)
        self.room.reserve()
        self.assertEqual(self.hotel.available_rooms_count(), 0)
