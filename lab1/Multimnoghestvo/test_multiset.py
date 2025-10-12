import unittest
from multiset import Multiset

class TestMultiset(unittest.TestCase):

    def test_empty_multiset(self):
        m = Multiset("{}")
        self.assertTrue(m.is_empty())
        self.assertEqual(m.size(), 0)

    def test_parse_nested(self):
        m = Multiset("{a, a, c, {a, b, b}, {}, {a, {c, c}}}")
        self.assertIn("a", m)
        self.assertIn("c", m)
        self.assertEqual(m.size(), 9) 

    def test_add_and_remove(self):
        m = Multiset("{}")
        m.add("x")
        self.assertIn("x", m)
        m.remove("x")
        self.assertNotIn("x", m)
        with self.assertRaises(ValueError):
            m.remove("x")

    def test_add_wrong_type(self):
        m = Multiset()
        with self.assertRaises(TypeError):
            m.add(123)  # не строка и не Multiset

    def test_union(self):
        m1 = Multiset("{a, b}")
        m2 = Multiset("{b, c}")
        result = m1 + m2
        self.assertIn("a", result)
        self.assertIn("b", result)
        self.assertIn("c", result)

        m1 += m2
        self.assertEqual(m1.size(), 4)

    def test_intersection(self):
        m1 = Multiset("{a, b}")
        m2 = Multiset("{b, c}")
        result = m1 * m2
        self.assertEqual(result.size(), 1)
        self.assertIn("b", result)

        m1 *= m2
        self.assertEqual(m1.size(), 1)

    def test_difference(self):
        m1 = Multiset("{a, b, c}")
        m2 = Multiset("{b}")
        result = m1 - m2
        self.assertNotIn("b", result)
        self.assertIn("a", result)

        m1 -= m2
        self.assertNotIn("b", m1)

    def test_contains_nested(self):
        nested = Multiset("{c}")
        m = Multiset("{a, {c}}")
        self.assertIn(nested, m)
        self.assertIn("c", m)

    def test_to_boolean(self):
        m = Multiset("{a, b}")
        boolean = m.to_boolean()
        boolean_str = str(boolean)
        self.assertIn("{}", boolean_str)
        self.assertIn("a", boolean_str)
        self.assertIn("b", boolean_str)

    def test_str_repr(self):
        m = Multiset("{a, b}")
        self.assertEqual(str(m), "{a, b}")
        self.assertEqual(repr(m), "{a, b}")

if __name__ == '__main__':
    unittest.main()
