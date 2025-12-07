# demo_main.py
# Консольная демонстрация проекта "Книжный склад"
from Core_Domains.Order_Processing.exceptions import OrderNotFound
from Core_Domains.book_catalog.models import Book
from Core_Domains.book_catalog.exceptions import BookNotFound
from Core_Domains.book_catalog.value_objects import Price
from Core_Domains.User_Security.exceptions import EmailAlreadyExists, WrongPassword, InvalidCredentials

from Core_Domains.Order_Processing.models import Order

from Core_Domains.Warehouse.models import Cell, StockItem
from Core_Domains.Warehouse.value_objects import Quantity

from Core_Domains.User_Security.models import User
from Infrastructure.Persistence_Layer.in_memory.book_repo import InMemoryBookRepository

book_repo = InMemoryBookRepository()
# === Используем зависимости из DI ===
from Infrastructure.api.dependencies import (
    get_book_service,
    get_order_service,
    get_payment_service,
    get_user_service,
    get_auth_service,
    get_warehouse_service,
)


book_service = get_book_service()
order_service = get_order_service()
payment_service = get_payment_service()
user_service = get_user_service()
auth_service = get_auth_service()
warehouse_service = get_warehouse_service()


# ------------------------------------------------------
#                   МЕНЮ
# ------------------------------------------------------

def menu():
    print("\n=== Книжный склад ===")
    print("1. Добавить книгу")
    print("2. Поиск книги")
    print("3. Создать заказ")
    print("4. Добавить книгу в заказ")
    print("5. Оплатить заказ")
    print("6. Регистрация пользователя")
    print("7. Логин пользователя")
    print("8. Приём товара на склад (inbound)")
    print("9. Перемещение товара между ячейками")
    print("10. Показать остатки по ячейке")
    print("11. Вывести все книги")
    print("12. Вывести все ячейки склада")
    print("13. Текущие незавершённые заказы (Корзина пользователя)")
    print("0. Выход")
    return input("Выберите действие: ")


# ------------------------------------------------------
#                   ФУНКЦИИ
# ------------------------------------------------------

def add_book():
    print("\n=== Добавить книгу ===")
    book_id = int(input("ID книги: "))
    title = input("Название: ")
    price = float(input("Цена: "))
    book = Book(
        id=book_id,
        title=title,
        authors=[],
        genre=None,
        publisher=None,
        edition=None,
        price=Price(price),
    )
    book_service.add_book(book)
    print("Книга добавлена.")


def search_book():
    print("\n=== Поиск книги ===")
    title = input("Название (или часть): ")
    books = book_service.search(title=title)
    if not books:
        print("Ничего не найдено.")
        return
    for b in books:
        print(f"[{b.id}] {b.title} — {b.price.amount} р.")


def create_order():
    print("\n=== Создать заказ ===")
    cid = int(input("ID покупателя: "))
    order = order_service.create_order(cid)
    print(f"Заказ создан. ID = {order.id}")


def add_book_to_order():
    print("\n=== Добавить книгу в заказ ===")

    while True:
        try:
            order_id = int(input("ID заказа: "))
            book_id = int(input("ID книги: "))
            qty = int(input("Количество: "))

            try:
                order_service.add_book(order_id, book_id, qty)
                print("Добавлено.")
                return

            except OrderNotFound:
                print(f"❌ Заказ с ID {order_id} не найден.")
                retry = input("Попробовать снова? (y/n): ").lower()
                if retry != "y":
                    return
                continue

            except BookNotFound:
                print(f"❌ Книга с ID {book_id} не найдена.")
                retry = input("Попробовать снова? (y/n): ").lower()
                if retry != "y":
                    return
                continue

            except KeyError:
                # на случай, если репо выбросит KeyError напрямую
                print(f"❌ Книга с ID {book_id} отсутствует в каталоге.")
                retry = input("Попробовать снова? (y/n): ").lower()
                if retry != "y":
                    return
                continue

        except ValueError:
            print("❌ Ошибка ввода. Введите числа.")
            continue


def pay_order():
    print("\n=== Оплатить заказ ===")
    order_id = int(input("ID заказа: "))
    order_service.pay(order_id)
    print("Заказ оплачен.")


def register_user():
    print("\n=== Регистрация ===")

    while True:
        email = input("Email: ").strip()
        pwd = input("Пароль: ").strip()

        try:
            user = user_service.register(email, pwd)
            print(f"Пользователь создан. ID = {user.id}")
            return


        except EmailAlreadyExists:
            print(f"Email '{email}' уже зарегистрирован.")
            retry = input("Попробовать снова? (y/n): ").lower()
            if retry != "y":
                return
            continue

        except WrongPassword:
            print("Пароль не соответствует требованиям.")
            retry = input("Попробовать снова? (y/n): ").lower()
            if retry != "y":
                return
            continue

        except Exception as ex:
            print(f"Неизвестная ошибка: {ex}")
            retry = input("Попробовать снова? (y/n): ").lower()
            if retry != "y":
                return
            continue


def login_user():
    print("\n=== Логин ===")
    email = input("Email: ").strip()
    pwd = input("Пароль: ").strip()

    try:
        user = auth_service.authenticate(email, pwd)
        print(f"Успешный вход! Добро пожаловать, {user.email}.")
    except InvalidCredentials:
        print("Неверный email или пароль.")
        retry = input("Попробовать снова? (y/n): ").strip().lower()
        if retry == "y":
            return login_user()
        else:
            return
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")



def inbound():
    print("\n=== Приём товара ===")
    book_id = int(input("ID книги: "))
    cell_id = int(input("ID ячейки: "))
    qty = int(input("Количество: "))

    # Если ячейки нет — создадим автоматически
    try:
        warehouse_service.cell_repo.get(cell_id)
    except:
        cell = Cell(
            id=cell_id,
            shelf_id=1,
            code=f"CELL-{cell_id}",
            capacity=999,
            description="Автосозданная ячейка"
        )
        warehouse_service.cell_repo.save(cell)

    warehouse_service.inbound(book_id, cell_id, qty)
    print("Приёмка выполнена.")


def relocate():
    print("\n=== Перемещение ===")
    book_id = int(input("ID книги: "))
    from_cell = int(input("Из ячейки: "))
    to_cell = int(input("В ячейку: "))
    qty = int(input("Количество: "))
    warehouse_service.relocate(book_id, from_cell, to_cell, qty)
    print("Перемещено.")


def show_stock():
    print("\n=== Остатки по ячейке ===")
    cell_id = int(input("ID ячейки: "))
    stock = warehouse_service.stock_repo.list_by_cell(cell_id)
    if not stock:
        print("Пусто.")
        return
    for s in stock:
        print(f"Книга {s.book_id}: {s.quantity.amount} шт.")

def show_all_books():
    print("\n=== Все книги ===")
    for b in book_service.list_all():
        print(f"{b.id}: {b.title} — {b.price.amount}р")

def show_all_cells():
    print("\n=== Ячейки склада ===")
    for cell in warehouse_service.list_cells():
        print(f"{cell.id}: {cell.code} (capacity={cell.capacity})")
def show_user_cart():
    print("\n=== Корзина пользователя ===")
    try:
        user_id = int(input("ID пользователя: "))
    except:
        print("Неверный ввод.")
        return

    # 1️⃣ Получаем корзину как есть (старый/новый)
    order = order_service.order_repo.find_open_cart(user_id)
    if not order:
        print("Корзина пуста.")
        return

    # 2️⃣ Аккуратно вычисляем ID заказа
    order_id = getattr(order, "order_id", getattr(order, "id", None))
    print(f"Корзина (Order id={order_id}):")

    # 3️⃣ Для безопасности — пробуем получить книгу по item.book или item.book_id
    for item in getattr(order, "items", []):
        # сначала пробуем item.book → Book
        book = getattr(item, "book", None)

        # если книга не указана напрямую, пробуем вытащить id
        if book is None:
            # item.book_id в одних моделях, item.id_book — в других
            book_id = getattr(item, "book_id", getattr(item, "id_book", None))
            if book_id is not None:
                book = book_service.book_repo.get(book_id)
        else:
            # если объект есть — пробуем взять его id
            book_id = getattr(book, "book_id", getattr(book, "id", None))

        # если после всех попыток книга не найдена
        if not book:
            book_title = "Неизвестная книга"
            book_id = None
        else:
            book_title = getattr(book, "title", "???")
            book_id = getattr(book, "book_id", getattr(book, "id", None))

        print(f"- {book_title} (book_id={book_id}), qty={item.quantity}")




# ------------------------------------------------------
#                   MAIN LOOP
# ------------------------------------------------------

def main():
    while True:
        choice = menu()
        if choice == "1":
            add_book()
        elif choice == "2":
            search_book()
        elif choice == "3":
            create_order()
        elif choice == "4":
            add_book_to_order()
        elif choice == "5":
            pay_order()
        elif choice == "6":
            register_user()
        elif choice == "7":
            login_user()
        elif choice == "8":
            inbound()
        elif choice == "9":
            relocate()
        elif choice == "10":
            show_stock()
        elif choice == "11":
            show_all_books()
        elif choice == "12":
            show_all_cells()
        elif choice == "13":
            show_user_cart()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неверный ввод.")


if __name__ == "__main__":
    main()
