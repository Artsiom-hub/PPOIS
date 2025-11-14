import unittest
from sort_container import SortContainer


class TestSortContainerBasic(unittest.TestCase):



    def test_default_constructor(self):
        c = SortContainer()
        self.assertTrue(c.empty())
        self.assertEqual(c.size(), 0)

    def test_constructor_from_iterable(self):
        c = SortContainer([1, 2, 3])
        self.assertFalse(c.empty())
        self.assertEqual(c.size(), 3)
        self.assertEqual(c[0], 1)
        self.assertEqual(c[2], 3)

    def test_copy_constructor(self):
        c1 = SortContainer([10, 20, 30])
        c2 = SortContainer.copy(c1)
        self.assertEqual(list(c1), list(c2))
        c2.push_back(40)
        self.assertNotEqual(list(c1), list(c2))


    def test_empty(self):
        c = SortContainer()
        self.assertTrue(c.empty())
        c.push_back(1)
        self.assertFalse(c.empty())

    def test_clear(self):
        c = SortContainer([1, 2, 3])
        c.clear()
        self.assertTrue(c.empty())
        self.assertEqual(c.size(), 0)



    def test_at_valid(self):
        c = SortContainer([5, 6, 7])
        self.assertEqual(c.at(1), 6)

    def test_at_invalid(self):
        c = SortContainer([1, 2])
        with self.assertRaises(IndexError):
            c.at(5)

    def test_front(self):
        c = SortContainer([10, 20, 30])
        self.assertEqual(c.front(), 10)

    def test_front_empty(self):
        c = SortContainer()
        with self.assertRaises(IndexError):
            c.front()

    def test_back(self):
        c = SortContainer([10, 20, 30])
        self.assertEqual(c.back(), 30)

    def test_back_empty(self):
        c = SortContainer()
        with self.assertRaises(IndexError):
            c.back()

    def test_getitem(self):
        c = SortContainer([1, 2, 3])
        self.assertEqual(c[1], 2)

    def test_setitem(self):
        c = SortContainer([1, 2, 3])
        c[1] = 99
        self.assertEqual(c[1], 99)


    def test_push_back(self):
        c = SortContainer()
        c.push_back(5)
        c.push_back(7)
        self.assertEqual(list(c), [5, 7])

    def test_pop_back(self):
        c = SortContainer([10, 20, 30])
        value = c.pop_back()
        self.assertEqual(value, 30)
        self.assertEqual(list(c), [10, 20])

    def test_pop_back_empty(self):
        c = SortContainer()
        with self.assertRaises(IndexError):
            c.pop_back()

    def test_insert_middle(self):
        c = SortContainer([1, 3, 4])
        c.insert(1, 2)
        self.assertEqual(list(c), [1, 2, 3, 4])

    def test_insert_front(self):
        c = SortContainer([2, 3])
        c.insert(0, 1)
        self.assertEqual(list(c), [1, 2, 3])

    def test_insert_back(self):
        c = SortContainer([1, 2])
        c.insert(2, 3)
        self.assertEqual(list(c), [1, 2, 3])

    def test_insert_invalid(self):
        c = SortContainer([1, 2])
        with self.assertRaises(IndexError):
            c.insert(5, 10)

    def test_erase_valid(self):
        c = SortContainer([1, 2, 3])
        c.erase(1)
        self.assertEqual(list(c), [1, 3])

    def test_erase_invalid(self):
        c = SortContainer([1])
        with self.assertRaises(IndexError):
            c.erase(2)



    def test_iterator(self):
        c = SortContainer([10, 20, 30])
        collected = [x for x in c]
        self.assertEqual(collected, [10, 20, 30])


    def test_comparison_equal(self):
        c1 = SortContainer([1, 2, 3])
        c2 = SortContainer([1, 2, 3])
        self.assertTrue(c1 == c2)
        self.assertFalse(c1 != c2)

    def test_comparison_lexicographic(self):
        c1 = SortContainer([1, 2, 3])
        c2 = SortContainer([1, 2, 4])
        self.assertTrue(c1 < c2)
        self.assertTrue(c2 > c1)
        self.assertTrue(c1 <= c2)
        self.assertTrue(c2 >= c1)



    def test_assign(self):
        c1 = SortContainer([10, 20, 30])
        c2 = SortContainer([1])
        c2.assign(c1)
        self.assertEqual(list(c2), [10, 20, 30])
        self.assertIsNot(c1, c2)

    def test_assign_self(self):
        c = SortContainer([1, 2, 3])
        c.assign(c)  
        self.assertEqual(list(c), [1, 2, 3])



    def test_str_output(self):
        c = SortContainer([1, 2, 3])
        self.assertEqual(str(c), "{1, 2, 3}")

    def test_str_empty(self):
        c = SortContainer()
        self.assertEqual(str(c), "{}")



    def test_begin_iterator(self):
        c = SortContainer([5, 6, 7])
        it = c.begin()
        self.assertEqual(next(it), 5)
        self.assertEqual(next(it), 6)

    def test_end_iterator_stop_iteration(self):
        c = SortContainer([10])
        it = c.end()
        with self.assertRaises(StopIteration):
            next(it)



    def test_iterator_manual(self):
        c = SortContainer([1, 2, 3])
        it = iter(c)
        self.assertEqual(next(it), 1)
        self.assertEqual(next(it), 2)
        self.assertEqual(next(it), 3)
        with self.assertRaises(StopIteration):
            next(it)


    def test_greater_than(self):
        c1 = SortContainer([1, 5, 7])
        c2 = SortContainer([1, 5, 6])
        self.assertTrue(c1 > c2)
        self.assertFalse(c2 > c1)

    def test_greater_equal(self):
        c1 = SortContainer([2, 3, 4])
        c2 = SortContainer([2, 3, 4])
        c3 = SortContainer([2, 3, 3])

        self.assertTrue(c1 >= c2)   
        self.assertTrue(c1 >= c3)  
        self.assertFalse(c3 >= c1)

    def test_comparison_not_sortcontainer(self):
        c = SortContainer([1, 2, 3])
        self.assertEqual(c.__gt__(123), NotImplemented)
        self.assertEqual(c.__ge__("abc"), NotImplemented)



    def test_repr(self):
        c = SortContainer([1, 2])
        r = repr(c)
        self.assertTrue("SortContainer" in r)
        self.assertTrue("[1, 2]" in r or "(1, 2)" in r)

  

    def test_bstnode_basic_sorted_output(self):
   
        c = SortContainer([5, 1, 3, 2])
        c.sort_binary_tree()
        self.assertEqual(list(c), [1, 2, 3, 5])

    def test_bstnode_handles_duplicates(self):
        c = SortContainer([3, 1, 3, 2])
        c.sort_binary_tree()
      
        self.assertEqual(list(c), [1, 2, 3, 3])

    def test_bstnode_single_element(self):
        c = SortContainer([42])
        c.sort_binary_tree()
        self.assertEqual(list(c), [42])

    def test_bstnode_empty(self):
        c = SortContainer()
        c.sort_binary_tree()   
        self.assertEqual(list(c), [])


    def test_bst_sort_numbers_basic(self):
        c = SortContainer([5, 3, 7, 1, 4])
        c.sort_binary_tree()
        self.assertEqual(list(c), [1, 3, 4, 5, 7])

    def test_bst_sort_numbers_with_duplicates(self):
        c = SortContainer([4, 2, 4, 3, 2])
        c.sort_binary_tree()
        self.assertEqual(list(c), [2, 2, 3, 4, 4])

    def test_bst_sort_single_element(self):
        c = SortContainer([42])
        c.sort_binary_tree()
        self.assertEqual(list(c), [42])

    def test_bst_sort_empty(self):
        c = SortContainer()
        c.sort_binary_tree()  
        self.assertEqual(list(c), [])

    def test_bst_sort_custom_objects(self):
        class P:
            def __init__(self, name, age):
                self.name = name
                self.age = age
            def __lt__(self, other):
                return self.age < other.age
            def __repr__(self):
                return f"{self.name}({self.age})"

        people = [
            P("Carl", 25),
            P("Bob", 22),
            P("Alice", 30),
        ]
        c = SortContainer(people)
        c.sort_binary_tree()
        names = [p.name for p in c]
        self.assertEqual(names, ["Bob", "Carl", "Alice"])


    def test_msd_sort_simple_strings(self):
        c = SortContainer(["ba", "ab", "aa"])
        c.sort_msd(key=lambda s: s)
        self.assertEqual(list(c), ["aa", "ab", "ba"])

    def test_msd_sort_strings_varlen(self):
        c = SortContainer(["b", "aa", "a"])
        c.sort_msd(key=lambda x: x)
        self.assertEqual(list(c), ["a", "aa", "b"])

    def test_msd_sort_custom_objects_by_name(self):
        class P:
            def __init__(self, name): self.name = name
            def __repr__(self): return self.name

        c = SortContainer([P("Carl"), P("Bob"), P("Alice")])
        c.sort_msd(key=lambda p: p.name)
        self.assertEqual([p.name for p in c], ["Alice", "Bob", "Carl"])

    def test_msd_sort_handles_prefix_case(self):
        c = SortContainer(["a", "ab", "abc", "b"])
        c.sort_msd(key=lambda x: x)
        self.assertEqual(list(c), ["a", "ab", "abc", "b"])

    def test_msd_sort_requires_key(self):
        c = SortContainer(["x", "y"])
        with self.assertRaises(TypeError):
            c.sort_msd()

    def test_msd_sort_key_must_return_string(self):
        c = SortContainer([1, 2, 3])
        with self.assertRaises(TypeError):
            c.sort_msd(key=lambda x: 123)

    def test_msd_sort_one_element(self):
        c = SortContainer(["hello"])
        c.sort_msd(key=lambda x: x)
        self.assertEqual(list(c), ["hello"])

    def test_msd_sort_empty(self):
        c = SortContainer()
        c.sort_msd(key=lambda x: x)  
        self.assertEqual(list(c), [])

    def test_msd_sort_duplicates(self):
        c = SortContainer(["bob", "bob", "alice"])
        c.sort_msd(key=lambda x: x)
        self.assertEqual(list(c), ["alice", "bob", "bob"])

    def test_msd_sort_unicode(self):
        c = SortContainer(["яблоко", "авто", "бета"])
        c.sort_msd(key=lambda x: x)
        self.assertEqual(list(c), ["авто", "бета", "яблоко"])


if __name__ == "__main__":
    unittest.main()
