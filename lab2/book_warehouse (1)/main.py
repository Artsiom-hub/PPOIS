from warehouse.models.core import IDGenerator, Credentials, PasswordHasher, User, Address
from warehouse.models.inventory import Author, Publisher, Category, Book, Shelf, Bin, InventoryItem, Warehouse
from warehouse.models.finance import Currency, Account, PaymentGateway
from warehouse.models.orders import Customer, Cart, OrderLine
from warehouse.services.payment_service import PaymentService
from warehouse.services.inventory_service import InventoryService
from warehouse.exceptions import WarehouseError

def setup_system():
    hasher = PasswordHasher(rounds=5)
    creds = Credentials(username="petrila", password_hash=hasher.hash("secret", "salt"), salt="salt")
    user = User(id="u1", name="Petrovich", role="customer", creds=creds)

    author = Author(id="a1", name="Terry Pratchett")
    pub = Publisher(id="p1", name="Transworld", address="UK")
    cat = Category(id="c1", name="Fantasy")
    book1 = Book(isbn="9780552161244", title="Going Postal", author=author, publisher=pub, price=12.50, category=cat)
    book2 = Book(isbn="9780552161251", title="Making Money", author=author, publisher=pub, price=13.00, category=cat)
    shelf = Shelf(id="s1", name="Fantasy Shelf", capacity=100)
    bin1 = Bin(id="b1", shelf=shelf, label="B-01")
    bin2 = Bin(id="b2", shelf=shelf, label="B-02")
    item1 = InventoryItem(book=book1, quantity=10, bin=bin1)
    item2 = InventoryItem(book=book2, quantity=8, bin=bin2)
    wh = Warehouse(id="w1", name="Main Warehouse")
    wh.put(item1)
    wh.put(item2)

    inv_service = InventoryService(warehouse=wh)

    eur = Currency(code="EUR", symbol="€", rate_to_usd=1.1)
    acc_src = Account(id="acc1", owner="Petrovich", currency=eur, balance=100.0)
    acc_dst = Account(id="acc2", owner="BookStore", currency=eur, balance=0.0)
    gateway = PaymentGateway(name="Stripe-ish", fee_rate=0.02)
    pay_service = PaymentService(gateway=gateway)

    customer = Customer(id="c1", user=user, address=Address(line1="Main 1", city="Helsinki", country="FI", postal_code="00100"))
    cart = Cart(customer=customer)

    return {
        "wh": wh,
        "inv_service": inv_service,
        "pay_service": pay_service,
        "customer": customer,
        "cart": cart,
        "acc_src": acc_src,
        "acc_dst": acc_dst
    }

def show_stock(wh):
    print("\n=== СКЛАД ===")
    for item in wh.bins.values():
        print(f"{item.book.isbn} | {item.book.title} | Остаток: {item.quantity} | Цена: {item.book.price} €")

def show_cart(cart):
    print("\n=== КОРЗИНА ===")
    if not cart.items:
        print("Пусто.")
        return
    for line in cart.items:
        print(f"{line.book.isbn} | {line.book.title} x{line.qty} = {line.total()} €")
    total = sum(l.total() for l in cart.items)
    print(f"Итого: {total} €")

def main():
    ctx = setup_system()
    gen = IDGenerator(prefix="ORD")
    while True:
        print("\n=== КНИЖНЫЙ СКЛАД ===")
        print("1. Посмотреть склад")
        print("2. Добавить книгу в корзину")
        print("3. Показать корзину")
        print("4. Оформить заказ")
        print("5. Баланс пользователя")
        print("6. Выйти")
        print("7. Пополнить счёт")
        print("8. Удалить книгу из корзины")
        print("9. Добавить книгу в склад")
        choice = input("Выбор: ").strip()

        if choice == "1":
            show_stock(ctx["wh"])

        elif choice == "2":
            show_stock(ctx["wh"])
            isbn = input("Введите ISBN книги: ").strip()
            try:
                qty = int(input("Количество: "))
            except ValueError:
                print("Некорректное число.")
                continue
            item = ctx["wh"].find_by_isbn(isbn)
            if not item:
                print("Нет такой книги.")
                continue
            if item.quantity < qty:
                print("Недостаточно на складе.")
                continue
            ctx["cart"].add(item.book, qty)
            print(f"Добавлено {qty} шт. '{item.book.title}' в корзину.")

        elif choice == "3":
            show_cart(ctx["cart"])

        elif choice == "4":
            if not ctx["cart"].items:
                print("Корзина пуста.")
                continue
            order = ctx["cart"].to_order(gen.next())
            total = order.total()
            try:
                for line in order.lines:
                    ctx["inv_service"].reserve(line.book.isbn, line.qty)
                tx = ctx["pay_service"].transfer(ctx["acc_src"], ctx["acc_dst"], total)
                order.mark("PAID")
                print(f"Заказ {order.id} оформлен! Списано {total} €, статус транзакции: {tx.status}")
                ctx["cart"].items.clear()
            except WarehouseError as e:
                print(f"Ошибка: {e.__class__.__name__} — {e}")

        elif choice == "5":
            print(f"Баланс Петровича: {ctx['acc_src'].balance} €, Магазина: {ctx['acc_dst'].balance} €")

        elif choice == "6":
            print("Выход.")
            break

        elif choice == "7":
            try:
                amount = float(input("Введите сумму пополнения (€): "))
                ctx["acc_src"].deposit(amount)
                print(f"Счёт пополнен на {amount} €, новый баланс: {ctx['acc_src'].balance} €")
            except ValueError:
                print("Ошибка: некорректная сумма.")

        elif choice == "8":
            show_cart(ctx["cart"])
            isbn = input("Введите ISBN для удаления: ").strip()
            before = len(ctx["cart"].items)
            ctx["cart"].items = [i for i in ctx["cart"].items if i.book.isbn != isbn]
            after = len(ctx["cart"].items)
            if before == after:
                print("Такой книги нет в корзине.")
            else:
                print("Удалено из корзины.")

        elif choice == "9":
            isbn = input("ISBN новой книги: ").strip()
            title = input("Название: ").strip()
            try:
                price = float(input("Цена (€): "))
                qty = int(input("Количество: "))
            except ValueError:
                print("Ошибка: некорректные данные.")
                continue
            author = Author(id=f"a_{isbn}", name="Unknown Author")
            pub = Publisher(id=f"p_{isbn}", name="SelfPub", address="Unknown")
            cat = Category(id=f"c_{isbn}", name="General")
            new_book = Book(isbn=isbn, title=title, author=author, publisher=pub, price=price, category=cat)
            new_bin = Bin(id=f"b_{isbn}", shelf=next(iter(ctx["wh"].bins.values())).bin.shelf, label=f"B-{isbn}")
            new_item = InventoryItem(book=new_book, quantity=qty, bin=new_bin)
            ctx["wh"].put(new_item)
            print(f"Добавлена книга '{title}' ({qty} шт.) в склад.")

        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()
