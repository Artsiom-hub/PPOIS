from __future__ import annotations
from typing import (
    TypeVar,
    Generic,
    Iterable,
    Iterator,
    Callable,
    List,
    Optional,
    Any,
)

T = TypeVar("T")


class SortContainer(Generic[T]):

    value_type = T # type: ignore
    reference = T # type: ignore
    const_reference = T # type: ignore
    pointer = T # type: ignore
    const_pointer = T # type: ignore
    size_type = int
    difference_type = int

    class _Iterator(Iterator[T]):
        def __init__(self, data: List[T], index: int = 0):
            self._data = data
            self._index = index

        def __next__(self) -> T:
            if self._index >= len(self._data):
                raise StopIteration
            value = self._data[self._index]
            self._index += 1
            return value

        def __iter__(self) -> "SortContainer._Iterator":
            return self



    def __init__(self, iterable: Optional[Iterable[T]] = None) -> None:

        self._data: List[T] = []
        if iterable is not None:
            for x in iterable:
                self._data.append(x)

    @classmethod
    def copy(cls, other: "SortContainer[T]") -> "SortContainer[T]":

        return cls(other._data)

    def __del__(self):

        self.clear()

 
    def empty(self) -> bool:

        return len(self._data) == 0

    def clear(self) -> None:

        self._data.clear()

    def size(self) -> int:
        return len(self._data)



    def at(self, index: int) -> T:

        if index < 0 or index >= len(self._data):
            raise IndexError("index out of range")
        return self._data[index]

    def front(self) -> T:
        if self.empty():
            raise IndexError("container is empty")
        return self._data[0]

    def back(self) -> T:
        if self.empty():
            raise IndexError("container is empty")
        return self._data[-1]

    def __getitem__(self, index: int) -> T:
        return self._data[index]

    def __setitem__(self, index: int, value: T) -> None:
        self._data[index] = value



    def push_back(self, value: T) -> None:
        self._data.append(value)

    def pop_back(self) -> T:
        if self.empty():
            raise IndexError("pop_back from empty container")
        return self._data.pop()

    def insert(self, index: int, value: T) -> None:
        if index < 0 or index > len(self._data):
            raise IndexError("insert position out of range")
        self._data.insert(index, value)

    def erase(self, index: int) -> None:
        if index < 0 or index >= len(self._data):
            raise IndexError("erase position out of range")
        del self._data[index]



    def begin(self) -> "SortContainer._Iterator":
        return SortContainer._Iterator(self._data, 0)

    def end(self) -> "SortContainer._Iterator":

        return SortContainer._Iterator(self._data, len(self._data))

    def __iter__(self) -> "SortContainer._Iterator":
        return self.begin()

 

    def assign(self, other: "SortContainer[T]") -> "SortContainer[T]":
        """Аналог operator= из C++."""
        if self is other:
            return self
        self._data = list(other._data)
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SortContainer):
            return NotImplemented
        return self._data == other._data

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SortContainer):
            return NotImplemented
        return self._data != other._data

    def __lt__(self, other: "SortContainer[T]") -> bool:
        if not isinstance(other, SortContainer):
            return NotImplemented
        return self._data < other._data

    def __le__(self, other: "SortContainer[T]") -> bool:
        if not isinstance(other, SortContainer):
            return NotImplemented
        return self._data <= other._data

    def __gt__(self, other: "SortContainer[T]") -> bool:
        if not isinstance(other, SortContainer):
            return NotImplemented
        return self._data > other._data

    def __ge__(self, other: "SortContainer[T]") -> bool:
        if not isinstance(other, SortContainer):
            return NotImplemented
        return self._data >= other._data



    def __str__(self) -> str:

        return "{" + ", ".join(str(x) for x in self) + "}"

    def __repr__(self) -> str:
        return f"SortContainer({self._data!r})"



    class _BSTNode(Generic[T]):
        __slots__ = ("value", "left", "right")

        def __init__(self, value: T) -> None:
            self.value: T = value
            self.left: Optional["SortContainer._BSTNode[T]"] = None
            self.right: Optional["SortContainer._BSTNode[T]"] = None

        def insert(self, value: T) -> None:
            if value < self.value:  
                if self.left is None:
                    self.left = SortContainer._BSTNode(value)
                else:
                    self.left.insert(value)
            else:
                if self.right is None:
                    self.right = SortContainer._BSTNode(value)
                else:
                    self.right.insert(value)

        def inorder(self, out: List[T]) -> None:
            if self.left:
                self.left.inorder(out)
            out.append(self.value)
            if self.right:
                self.right.inorder(out)

    def sort_binary_tree(self) -> None:

        if self.empty():
            return

        # строим дерево
        it = iter(self._data)
        root = SortContainer._BSTNode(next(it))
        for v in it:
            root.insert(v)


        result: List[T] = []
        root.inorder(result)
        self._data = result



    def sort_msd(self, key: Optional[Callable[[T], str]] = None) -> None:

        if key is None:
            raise TypeError("sort_msd requires a 'key' function returning str")


        keyed: List[tuple[str, T]] = [(key(v), v) for v in self._data]

        def msd_bucket_sort(arr: List[tuple[str, T]], pos: int) -> List[tuple[str, T]]:
            if len(arr) <= 1:
                return arr


            buckets: dict[Optional[str], List[tuple[str, T]]] = {}
            for k, v in arr:
                ch: Optional[str]
                if pos >= len(k):
                    ch = None 
                else:
                    ch = k[pos]
                if ch not in buckets:
                    buckets[ch] = []
                buckets[ch].append((k, v))


            keys_sorted = sorted(
                buckets.keys(),
                key=lambda c: (1, c) if c is not None else (0, ""),
            )

            result: List[tuple[str, T]] = []
            for bk in keys_sorted:
                sub = buckets[bk]
                if bk is None:
                    
                    result.extend(sub)
                else:
                   
                    result.extend(msd_bucket_sort(sub, pos + 1))
            return result

        sorted_pairs = msd_bucket_sort(keyed, 0)
        self._data = [v for _, v in sorted_pairs]




if __name__ == "__main__":
    class Person:
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

        def __lt__(self, other: "Person") -> bool:
            return self.age < other.age

        def __repr__(self) -> str:
            return f"{self.name}({self.age})"

    people = SortContainer[Person]([
        Person("Alice", 30),
        Person("Bob", 22),
        Person("Carl", 25),
    ])

    print("Исходный контейнер:", people)

   
    c1 = SortContainer.copy(people)
    c1.sort_binary_tree()
    print("После binary tree sort:", c1)

  
    c2 = SortContainer.copy(people)
    c2.sort_msd(key=lambda p: p.name)
    print("После MSD radix sort (по имени):", c2)

  
    print("c1 < c2 ?", c1 < c2)
    print("Итерируем c1:", [p for p in c1])
