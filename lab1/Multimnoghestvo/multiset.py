class Multiset:
    def __init__(self, data=None):
        self.elements = []

        if isinstance(data, str):
            self.elements = self._parse_multiset(data.strip())
        elif isinstance(data, list):
            self.elements = data
        elif isinstance(data, Multiset):
            self.elements = [elem for elem in data.elements]


    def _parse_multiset(self, s):
        s = s.strip()
        if not (s.startswith('{') and s.endswith('}')):
            raise ValueError("Множество должно быть заключено в фигурные скобки")

        s = s[1:-1].strip()
        if not s:
            return []

        result = []
        i = 0
        while i < len(s):
            if s[i] == '{':
                start = i
                depth = 1
                i += 1
                while i < len(s) and depth > 0:
                    if s[i] == '{':
                        depth += 1
                    elif s[i] == '}':
                        depth -= 1
                    i += 1
                if depth != 0:
                    raise ValueError("Некорректная структура скобок")
                nested = s[start:i]
                result.append(Multiset(nested))
            elif s[i] == ',':
                i += 1
            else:
                start = i
                while i < len(s) and s[i] not in {',', '{', '}'}:
                    i += 1
                token = s[start:i].strip()
                if token:
                    result.append(token)
        return result

    def is_empty(self):
        return len(self.elements) == 0

    def add(self, element):
        if isinstance(element, (str, Multiset)):
            self.elements.append(element)
        else:
            raise TypeError("Элемент должен быть строкой или множеством")

    def remove(self, element):
        for i, elem in enumerate(self.elements):
            if elem == element:
                del self.elements[i]
                return
        raise ValueError("Элемент не найден")

    def size(self):
        return sum(elem.size() if isinstance(elem, Multiset) else 1 for elem in self.elements)

    def __contains__(self, item):
        for elem in self.elements:
            if elem == item:
                return True
            if isinstance(elem, Multiset) and item in elem:
                return True
        return False

    def __add__(self, other):
        return Multiset(self.elements + other.elements)

    def __iadd__(self, other):
        self.elements.extend(other.elements)
        return self

    def __mul__(self, other):
        result = []
        temp_other = other.elements.copy()
        for elem in self.elements:
            if elem in temp_other:
                result.append(elem)
                temp_other.remove(elem)
        return Multiset(result)

    def __imul__(self, other):
        self.elements = (self * other).elements
        return self

    def __sub__(self, other):
        result = self.elements.copy()
        for elem in other.elements:
            if elem in result:
                result.remove(elem)
        return Multiset(result)

    def __isub__(self, other):
        self.elements = (self - other).elements
        return self

    def to_boolean(self):
        unique_elements = []
        for elem in self.elements:
            if elem not in unique_elements:
                unique_elements.append(elem)

        def generate_subsets(arr, index=0):
            if index == len(arr):
                return [Multiset()]
            subsets = generate_subsets(arr, index + 1)
            current_elem = arr[index]
            new_subsets = []
            for subset in subsets:
                with_elem = Multiset(subset.elements + [current_elem])
                new_subsets.append(with_elem)
            return subsets + new_subsets

        return Multiset(generate_subsets(unique_elements))

    def __str__(self):
        parts = []
        for elem in self.elements:
            parts.append(str(elem) if isinstance(elem, Multiset) else elem)
        return "{" + ", ".join(parts) + "}"

    def __repr__(self):
        return self.__str__()
    def __eq__(self, other):

        if not isinstance(other, Multiset):
            return False
        if len(self.elements) != len(other.elements):
            return False


        temp_other = other.elements.copy()

        for elem in self.elements:
            if elem in temp_other:
                temp_other.remove(elem)
            else:
                return False
        return True

    def __hash__(self):

        return id(self)  

