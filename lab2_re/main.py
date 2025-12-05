# demo_main.py
# Консольная демонстрация проекта "Книжный склад"

from Core_Domains.book_catalog.models import Book
from Core_Domains.book_catalog.value_objects import Price

from Core_Domains.Order_Processing.models import Order

from Core_Domains.Warehouse.models import Cell, StockItem
from Core_Domains.Warehouse.value_objects import Quantity

from Core_Domains.User_Security.models import User

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
    order_id = int(input("ID заказа: "))
    book_id = int(input("ID книги: "))
    qty = int(input("Количество: "))
    order_service.add_book(order_id, book_id, qty)
    print("Добавлено.")


def pay_order():
    print("\n=== Оплатить заказ ===")
    order_id = int(input("ID заказа: "))
    order_service.pay(order_id)
    print("Заказ оплачен.")


def register_user():
    print("\n=== Регистрация ===")
    email = input("Email: ")
    pwd = input("Пароль: ")
    user = user_service.register(email, pwd)
    print(f"Пользователь создан. ID = {user.id}")


def login_user():
    print("\n=== Логин ===")
    email = input("Email: ")
    pwd = input("Пароль: ")
    user = auth_service.authenticate(email, pwd)
    print(f"Вход выполнен. ID пользователя = {user.id}")


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
    uid = int(input("ID пользователя: "))
    cart = order_service.get_user_cart(uid)
    if not cart:
        print("Корзина пустая.")
        return
    print(f"Корзина (Order id={cart.id}):")
    for item in cart.items:
        print(f"- book_id={item.book_id}, qty={item.quantity}")

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
