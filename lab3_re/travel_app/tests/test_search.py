import unittest
import datetime

from core.search.criteria import SearchCriteria
from core.search.recommendations import RecommendationEngine
from core.geography.locations import Country, City
from core.geography.destinations import Destination
from core.exceptions.travel_errors import InvalidSearchCriteriaError
from core.users.models import Customer


class TestSearchCriteria(unittest.TestCase):
    def setUp(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        self.airport = city.country.airports

    def test_missing_fields(self):
        crit = SearchCriteria()
        with self.assertRaises(InvalidSearchCriteriaError):
            crit.validate()

    def test_same_origin_dest(self):
        country = Country("DE", "Germany", "EUR")
        city = City("Berlin", country)
        airport = None
        # need real airport
        # create one
        from core.geography.airports import Airport
        airport = Airport("BER", "Berlin", city)

        crit = SearchCriteria(origin=airport, destination=airport)
        with self.assertRaises(InvalidSearchCriteriaError):
            crit.validate()


class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        country = Country("ES", "Spain", "EUR")
        city = City("Madrid", country)
        self.dest1 = Destination("MAD", city, "nice", tags=["food", "sun"])
        self.dest2 = Destination("BAR", city, "beach", tags=["beach", "sun"])
        self.dest3 = Destination("IBZ", city, "party", tags=["party"])

        self.customer = Customer("c1", "mail", "hash")
        self.engine = RecommendationEngine()

    def test_recommend(self):
        self.engine.add_history(self.customer, self.dest1)
        result = self.engine.recommend(self.customer, [self.dest1, self.dest2, self.dest3])
        self.assertIn(self.dest2, result)
        self.assertNotIn(self.dest3, result)
