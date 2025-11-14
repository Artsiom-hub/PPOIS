import unittest
from multiset import Multiset


class TestMultiset(unittest.TestCase):


    def test_init_empty(self):
        ms = Multiset()
        self.assertTrue(ms.is_empty())

    def test_init_from_list(self):
        ms = Multiset(["a", "b", "c"])
        self.assertEqual(ms.elements, ["a", "b", "c"])

    def test_init_from_string_simple(self):
        ms = Multiset("{a, b, c}")
        self.assertEqual(ms.elements, ["a", "b", "c"])

    def test_init_from_string_nested(self):
        ms = Multiset("{a, {b, c}, d}")
        self.assertEqual(
            ms.elements,
            ["a", Multiset("{b, c}"), "d"]
        )

    def test_init_invalid_no_braces(self):
        with self.assertRaises(ValueError):
            Multiset("a, b, c")

    def test_parse_unbalanced(self):
        with self.assertRaises(ValueError):
            Multiset("{a, {b, c}")

    # ---------- Методы ----------
    def test_is_empty_true(self):
        self.assertTrue(Multiset().is_empty())

    def test_is_empty_false(self):
        self.assertFalse(Multiset(["x"]).is_empty())

    def test_add_valid(self):
        ms = Multiset()
        ms.add("x")
        self.assertIn("x", ms.elements)

    def test_add_invalid_type(self):
        ms = Multiset()
        with self.assertRaises(TypeError):
            ms.add(123)

    def test_remove_existing(self):
        ms = Multiset(["a", "b"])
        ms.remove("a")
        self.assertEqual(ms.elements, ["b"])

    def test_remove_missing(self):
        ms = Multiset(["x"])
        with self.assertRaises(ValueError):
            ms.remove("y")

    def test_size_flat(self):
        ms = Multiset(["a", "b", "c"])
        self.assertEqual(ms.size(), 3)

    def test_size_nested(self):
        ms = Multiset(["a", Multiset(["b", "c"])])
        self.assertEqual(ms.size(), 3)

 
    def test_add_operator(self):
        ms1 = Multiset(["a"])
        ms2 = Multiset(["b"])
        ms3 = ms1 + ms2
        self.assertEqual(ms3, Multiset(["a", "b"]))

    def test_iadd_operator(self):
        ms1 = Multiset(["a"])
        ms2 = Multiset(["b"])
        ms1 += ms2
        self.assertEqual(ms1, Multiset(["a", "b"]))


    def test_mul_operator(self):
        ms1 = Multiset(["a", "b", "b", "c"])
        ms2 = Multiset(["b", "b", "x"])
        self.assertEqual(ms1 * ms2, Multiset(["b", "b"]))

    def test_imul_operator(self):
        ms1 = Multiset(["a", "b", "c"])
        ms2 = Multiset(["b"])
        ms1 *= ms2
        self.assertEqual(ms1, Multiset(["b"]))

 
    def test_sub_operator(self):
        ms1 = Multiset(["a", "b", "b"])
        ms2 = Multiset(["b"])
        self.assertEqual(ms1 - ms2, Multiset(["a", "b"]))

    def test_isub_operator(self):
        ms1 = Multiset(["a", "b"])
        ms2 = Multiset(["a"])
        ms1 -= ms2
        self.assertEqual(ms1, Multiset(["b"]))

  
    def test_contains_simple(self):
        ms = Multiset(["a", "b"])
        self.assertTrue("a" in ms)
        self.assertFalse("x" in ms)

    def test_contains_nested(self):
        ms = Multiset(["a", Multiset(["b", "c"])])
        self.assertTrue("b" in ms)
        self.assertFalse("x" in ms)


    def test_to_boolean(self):
        ms = Multiset(["a", "b"])
        boolean_ms = ms.to_boolean()

   
        self.assertEqual(len(boolean_ms.elements), 4)

     
        for el in boolean_ms.elements:
            self.assertIsInstance(el, Multiset)

  
    def test_str_representation(self):
        ms = Multiset(["a", Multiset(["b"])])
        self.assertEqual(str(ms), "{a, {b}}")

   
    def test_eq_true(self):
        self.assertEqual(
            Multiset(["a", "b", "b"]),
            Multiset(["b", "a", "b"])
        )

    def test_eq_false(self):
        self.assertNotEqual(
            Multiset(["a", "b"]),
            Multiset(["a", "b", "b"])
        )


    def test_hash_returns_id(self):
        ms = Multiset(["x"])
        self.assertEqual(hash(ms), id(ms))


if __name__ == "__main__":
    unittest.main()
