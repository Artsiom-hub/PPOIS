from multiset import Multiset

def main():
    m1 = Multiset("{a, a, c, {a, b, b}, {}, {a, {c, c}}}")
    m2 = Multiset("{a, c, d}")
    print("Множество m1:", m1)
    print("Множество m2:", m2)
    print("Объединение:", m1 + m2)
    print("Пересечение:", m1 * m2)
    print("Разность:", m1 - m2)
    print("Мощность m1:", m1.size())
    print("Булеан m1:", m1.to_boolean())

if __name__ == "__main__":
    main()
