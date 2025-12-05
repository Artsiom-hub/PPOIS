import unittest

from core.geography.locations import Country, City
from core.geography.destinations import Destination
from core.geography.airports import Airport


class TestCountry(unittest.TestCase):
    def test_country_add_airport(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        airport = Airport("BER", "Brandenburg", city)
        country.add_airport(airport)
        self.assertEqual(country.airports[0].code, "BER")

    def test_find_airport(self):
        country = Country("ES", "Spain", "EUR")
        a1 = Airport("MAD", "Madrid", City("Madrid", country))
        a2 = Airport("BCN", "Barcelona", City("Barcelona", country))
        country.add_airport(a1)
        country.add_airport(a2)
        self.assertEqual(country.find_airport("BCN"), a2)


class TestCity(unittest.TestCase):
    def test_city_describe(self):
        country = Country("FR", "France", "EUR")
        city = City("Paris", country, population=2000000)
        self.assertEqual(city.describe(), "Paris, France. Population: 2000000")


class TestDestination(unittest.TestCase):
    def test_destination_tags(self):
        country = Country("JP", "Japan", "JPY")
        city = City("Tokyo", country)
        dest = Destination("TKY", city, "desc")

        dest.add_tag("food")
        dest.add_tag("anime")
        dest.add_tag("food")

        self.assertTrue(dest.has_tag("food"))
        self.assertEqual(len(dest.tags), 2)


class TestAirport(unittest.TestCase):
    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        self.airport = Airport("BER", "Berlin Brandenburg", city)

    def test_add_terminal(self):
        self.airport.add_terminal("T1")
        self.airport.add_terminal("T2")
        self.assertEqual(self.airport.terminals, ["T1", "T2"])

    def test_full_description(self):
        desc = self.airport.full_description()
        self.assertEqual(desc, "Berlin Brandenburg (BER), Berlin, DE")
