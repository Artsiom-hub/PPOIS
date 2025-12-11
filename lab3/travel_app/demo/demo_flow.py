# run_cli.py — интерактивное CLI-приложение для всего проекта
import os
import sys

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid

from core.users.auth import AuthenticationService
from core.users.models import Customer

from core.geography.locations import Country, City
from core.geography.airports import Airport
from core.geography.destinations import Destination

from core.flights.flights import Flight
from core.flights.seats import Seat
from core.flights.passengers import PassengerProfile, Baggage

from core.hotels.hotels import Hotel
from core.hotels.rooms import Room, RoomType

from core.bookings.flight_booking import FlightBooking
from core.bookings.hotel_booking import HotelBooking

from core.cart.cart import Cart
from core.cart.items import CartItem

from core.loyalty.program import LoyaltyProgram
from core.loyalty.account import LoyaltyAccount

from core.discounts.coupons import Coupon
from core.payments.models import BankAccount, PaymentCard
from core.payments.gateway import PaymentGateway
from datetime import datetime, UTC, timedelta, date




# -----------------------------------------------------
# ГЛОБАЛЬНЫЕ ОБЪЕКТЫ (как будто память приложения)
# -----------------------------------------------------
def safe_input(prompt: str) -> str:
    """Нормальный input, который не пропускает ввод случайно."""
    try:
        return input(prompt)
    except EOFError:
        return ""

auth = AuthenticationService()
users = {}
countries = []
flights = []
hotels = []
cart = None
loyalty = None
payment_gateway = PaymentGateway("DemoPay")
carts = {}


def pause():
    input("\nНажмите ENTER, чтобы продолжить...")


# -----------------------------------------------------
# 1. Регистрация / вход
# -----------------------------------------------------

def register_user():
    print("\n=== Регистрация пользователя ===")
    email = input("Email: ")
    full_name = input("Имя: ")
    password = input("Пароль: ")

    user = Customer(
        user_id=str(uuid.uuid4()),
        email=email,
        full_name=full_name,
        password_hash=auth.hash_password(password),
    )

    users[user.user_id] = user
    print("Пользователь создан:", user.user_id)


def login_user():
    print("\n=== Вход ===")
    email = input("Email: ")
    password = input("Пароль: ")

    user = next((u for u in users.values() if u.email == email), None)
    if not user:
        print("Пользователь не найден")
        return None

    try:
        session = auth.authenticate(user, password)
        print("Успешный вход!")
        return user
    except Exception as e:
        print("Ошибка:", e)
        return None


# -----------------------------------------------------
# 2. География
# -----------------------------------------------------

def create_country_city_airport():
    print("\n=== Создать страну/город/аэропорт ===")
    cname = input("Страна: ")
    code = input("Код страны: ")
    cur = input("Валюта: ")
    country = Country(code=code, name=cname, currency=cur)
    countries.append(country)

    cityname = input("Город: ")
    pop = int(input("Население: "))
    city = City(name=cityname, country=country, population=pop)

    airport_code = input("Код аэропорта: ")
    airport_name = input("Название аэропорта: ")
    airport = Airport(code=airport_code, name=airport_name, city=city)
    country.add_airport(airport)

    print("\nСоздано:")
    print(country)
    print(city)
    print(airport)


def list_countries():
    print("\n=== Все страны ===")
    for c in countries:
        print("-", c.code, c.name)
        for a in c.airports:
            print("    Аэропорт:", a.code, a.name)


# -----------------------------------------------------
# 3. Рейсы
# -----------------------------------------------------

def create_flight():
    print("\n=== Создать авиарейс ===")
    if not countries:
        print("Сначала создайте страны/аэропорты!")
        return

    print("Список аэропортов:")
    airports = [a for c in countries for a in c.airports]
    for i, a in enumerate(airports):
        print(i, a.full_description())

    def safe_index(prompt: str, max_value: int) -> int:
        while True:
            try:
                idx = int(input(prompt))
                if 0 <= idx < max_value:
                    return idx
                print(f"Введите число от 0 до {max_value - 1}")
            except ValueError:
                print("Введите корректное число.")

    # использование:
    origin_idx = safe_index("Откуда (номер): ", len(airports))
    dest_idx   = safe_index("Куда (номер): ", len(airports))


    dep = datetime.now(UTC) + timedelta(days=1)
    arr = dep + timedelta(hours=3)


    flight = Flight(
        flight_number=input("Номер рейса: "),
        origin=airports[origin_idx],
        destination=airports[dest_idx],
        departure_time=dep,
        arrival_time=arr,
        base_price=float(input("Базовая цена: ")),
    )

    print("Добавление мест (введите пустую строку для остановки):")
    while True:
        seat_no = input("Место (например 12A): ")
        if not seat_no:
            break
        seat_cls = "Economy"
        is_win = seat_no.endswith("A")
        flight.add_seat(Seat(seat_number=seat_no, seat_class=seat_cls, is_window=is_win))

    flights.append(flight)
    print("Рейс создан!")


def list_flights():
    print("\n=== Все рейсы ===")
    for f in flights:
        print("-", f.flight_number, f.origin.code, "→", f.destination.code,
              "Seats:", f.available_seats_count())


# -----------------------------------------------------
# 4. Отели
# -----------------------------------------------------

def create_hotel():
    print("\n=== Создать отель ===")
    if not countries:
        print("Сначала создайте географию!")
        return

    # выбор города
    all_cities = []
    for c in countries:
        for a in c.airports:
            all_cities.append(a.city)

    for i, c in enumerate(all_cities):
        print(i, c.describe())

    city_idx = int(input("Выберите город: "))
    city = all_cities[city_idx]

    hotel = Hotel(
        name=input("Название отеля: "),
        city=city,
    )

    hotels.append(hotel)
    print("Отель создан!")

    print("Добавление комнат:")
    while True:
        room_num = input("Номер комнаты (ENTER = стоп): ")
        if not room_num:
            break
        rt = RoomType(name="Standard", capacity=2, amenities=["WiFi"])
        room = Room(room_number=room_num, room_type=rt, price_per_night=120.0)
        hotel.add_room(room)
        print("Комната добавлена!")


def list_hotels():
    print("\n=== Все отели ===")
    for h in hotels:
        print("-", h.name, "в", h.city.name, "Комнат:", len(h.rooms))


# -----------------------------------------------------
# 5. Бронирование
# -----------------------------------------------------
def safe_index(prompt: str, max_value: int) -> int:
    while True:
        try:
            idx = int(input(prompt))
            if 0 <= idx < max_value:
                return idx
            print(f"Введите число от 0 до {max_value - 1}")
        except ValueError:
            print("Введите корректное число.")

def make_flight_booking(user):
    if not flights:
        print("Нет рейсов!")
        return

    list_flights()
    idx = safe_index("Какой рейс бронируем?: ", len(flights))
    flight = flights[idx]


    seat_no = input("Выберите место: ")
    seat = flight.reserve_seat(seat_no)

    passenger = PassengerProfile(
        customer=user,
        passport_number=input("Паспорт: "),
        nationality="???",
        date_of_birth=date(1990, 1, 1),
    )

    booking = FlightBooking(
        booking_id=str(uuid.uuid4()),
        customer=user,
        created_at = datetime.now(UTC),
        total_price=flight.base_price,
        flight=flight,
        passenger=passenger,
    )
    booking.assign_seat(seat)

    print("Бронирование создано, цена:", booking.total_price)
    return booking


def make_hotel_booking(user):
    if not hotels:
        print("Нет отелей!")
        return

    list_hotels()
    idx = int(input("Какой отель?: "))
    hotel = hotels[idx]

    room = hotel.rooms[0]
    today = date.today()
    booking = HotelBooking(
        booking_id=str(uuid.uuid4()),
        customer=user,
        created_at=datetime.now(UTC),
        total_price=room.price_per_night,
        hotel=hotel,
        room=room,
        check_in = today + timedelta(days=1),
        check_out = today + timedelta(days=3),

    )
    print("Бронирование создано:", booking.total_price)
    return booking


# -----------------------------------------------------
# 6. Корзина
# -----------------------------------------------------

def get_user_cart(user):
    """Гарантированно возвращает корзину пользователя."""
    global cart, carts

    if user.email not in carts:
        carts[user.email] = Cart(user)

    cart = carts[user.email]
    return cart

def add_to_cart(user, item_type, booking):
    cart = get_user_cart(user)

    cart.add_item(
        CartItem(
            item_type=item_type,
            reference=booking,
            price=booking.total_price
        )
    )

    print("Добавлено в корзину!")
def show_cart(user):
    cart = get_user_cart(user)

    print("\n=== Корзина ===")
    if not cart.items:
        print("Корзина пуста.")
        print()
        return

    for idx, item in enumerate(cart.items):
        print(f"{idx}. {item.item_type}: {item.reference} — {item.price}")

    print(f"ИТОГО: {cart.total()}")
    print()
def clear_cart(user):
    cart = get_user_cart(user)
    cart.items.clear()
    print("Корзина очищена!\n")
def cart_menu(user):
    while True:
        print("\n--- Корзина ---")
        print("1. Показать корзину")
        print("2. Очистить корзину")
        print("0. Назад")

        choice = input("> ").strip()

        if choice == "1":
            show_cart(user)
            input("ENTER для продолжения...")

        elif choice == "2":
            clear_cart(user)
            input("ENTER для продолжения...")

        elif choice == "0":
            return

        else:
            print("Неверный ввод.")

# -----------------------------------------------------
# 7. Оплата
# -----------------------------------------------------

def setup_payment(user):
    acc = BankAccount(
        iban="DE" + str(uuid.uuid4())[:6],
        owner_name=user.full_name,
        balance=500.0,
    )
    card = PaymentCard(
        card_number="4111 1111 1111 1111",
        owner=user,
        bank_account=acc,
        cvv="123",
        expiry_month=12,
        expiry_year=2035,
    )
    user.add_card(card)
    print("Платёжная карта добавлена!")


def pay():
    global cart, carts

    # Нет корзины вообще
    if cart is None:
        print("Нет корзины!")
        return

    # Корзина есть, но пуста
    if not cart.items:
        print("Корзина пуста — нечего оплачивать.")
        return

    user = cart.customer
    amount = cart.total()
    card = user.get_default_card()

    if card is None:
        print("У пользователя нет платёжной карты!")
        return

    try:
        # Совершаем оплату
        payment_gateway.transfer(card, card, amount)
        print("Оплата успешно проведена!")

        # Очищаем корзину
        cart.items.clear()
        carts[user.email] = cart  # сохраняем пустую корзину

        print("Корзина очищена после оплаты!")

    except Exception as e:
        print("Ошибка при оплате:", e)



# -----------------------------------------------------
# 8. Лояльность
# -----------------------------------------------------

def setup_loyalty(user):
    global loyalty
    program = LoyaltyProgram("SkyPoints", base_multiplier=1.5)
    program.add_level("SILVER", 300)
    program.add_level("GOLD", 1000)
    loyalty = LoyaltyAccount(user, program)
    user.loyalty_account = loyalty
    print("Лояльность включена!")


def show_loyalty():
    if not loyalty:
        print("Лояльность не настроена")
        return
    print("Баллы:", loyalty.points, "Уровень:", loyalty.level)


# -----------------------------------------------------
# 9. Главное меню
# -----------------------------------------------------

def main_menu(user):
    while True:
        print("\n=== Главное меню ===")
        print("1. География")
        print("2. Рейсы")
        print("3. Отели")
        print("4. Бронирования")
        print("5. Корзина")
        print("6. Оплата")
        print("7. Лояльность")
        print("0. Выход")

        choice = input("> ")

        if choice == "1":
            print("\n--- География ---")
            print("1. Создать")
            print("2. Показать")
            sub = input("> ")
            if sub == "1": create_country_city_airport()
            if sub == "2": list_countries()

        elif choice == "2":
            print("\n--- Рейсы ---")
            print("1. Создать рейс")
            print("2. Показать рейсы")
            sub = input("> ")
            if sub == "1": create_flight()
            if sub == "2": list_flights()

        elif choice == "3":
            print("\n--- Отели ---")
            print("1. Создать отель")
            print("2. Показать отели")
            sub = input("> ")
            if sub == "1": create_hotel()
            if sub == "2": list_hotels()

        elif choice == "4":
            print("\n--- Бронирование ---")
            print("1. Рейс")
            print("2. Отель")
            sub = input("> ")

            if sub == "1":
                b = make_flight_booking(user)
                if b:
                    add_to_cart(user, "FLIGHT", b)

            elif sub == "2":
                b = make_hotel_booking(user)
                if b:
                    add_to_cart(user, "HOTEL", b)


        elif choice == "5":
            cart_menu(user)


        elif choice == "6":
            print("\n--- Оплата ---")
            print("1. Добавить платёжную карту")
            print("2. Оплатить")
            sub = input("> ")
            if sub == "1": setup_payment(user)
            if sub == "2": pay()

        elif choice == "7":
            print("\n--- Лояльность ---")
            print("1. Включить")
            print("2. Показать")
            sub = input("> ")
            if sub == "1": setup_loyalty(user)
            if sub == "2": show_loyalty()

        elif choice == "0":
            return

        pause()


def main():
    while True:
        print("\n=== Стартовое меню ===")
        print("1. Регистрация")
        print("2. Вход")
        print("0. Выход")
        choice = input("> ")

        if choice == "1":
            register_user()
        elif choice == "2":
            user = login_user()
            if user:
                main_menu(user)
        elif choice == "0":
            break


if __name__ == "__main__":
    main()
