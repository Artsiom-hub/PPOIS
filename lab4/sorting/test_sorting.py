import unittest
from unittest.mock import patch
from BST import binary_tree_sort
from MSD import msd_radix_sort
from test import Person
import test


class TestTestPy(unittest.TestCase):

    def test_person_sorting_bst(self):
        people = [
            Person("Alice", 30),
            Person("Bob", 22),
            Person("Carl", 25)
        ]
        sorted_people = binary_tree_sort(people)
        ages = [p.age for p in sorted_people]
        self.assertEqual(ages, [22, 25, 30])

    def test_string_sort_bst(self):
        arr = ["zeta", "alpha", "beta"]
        self.assertEqual(binary_tree_sort(arr), sorted(arr))

    def test_string_sort_msd(self):
        arr = ["zeta", "alpha", "beta", "ab", "aba"]
        self.assertEqual(msd_radix_sort(arr), sorted(arr))

    @patch("builtins.print")
    def test_output_format(self, mock_print):
        from importlib import reload
        reload(test)

        # Проверяем, что хотя бы ОДНА строка содержит "BST:"
        any_bst = any("BST:" in call.args[0] for call in mock_print.call_args_list)
        self.assertTrue(any_bst)

    def test_person_repr(self):
        p = Person("Bob", 22)
        self.assertEqual(repr(p), "Bob (22)")

    def test_msd_with_key_on_person(self):
        people = [
            Person("Alice", 30),
            Person("Bob", 22),
            Person("Carl", 25)
        ]
        result = msd_radix_sort(people, key=lambda p: f"{p.age:03d}")
        ages = [p.age for p in result]
        self.assertEqual(ages, [22, 25, 30])


if __name__ == "__main__":
    unittest.main()
