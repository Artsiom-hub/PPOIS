from BST import *
from MSD import *
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __lt__(self, other):
        return self.age < other.age

    def __repr__(self):
        return f"{self.name} ({self.age})"
people = [
    Person("Alice", 30),
    Person("Bob", 22),
    Person("Carl", 25)
]

sorted_people = binary_tree_sort(people)
sorted_people_M = msd_radix_sort(people)
print("BST:", sorted_people)
print("MSD:", sorted_people)


s = ["zeta", "alpha", "beta", "ab", "aba"]
print("BST:", binary_tree_sort(s))
print("MSD:",msd_radix_sort(s))
