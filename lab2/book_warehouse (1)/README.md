# Book Warehouse (Python)

Мини-проект демонстрирует ООП-архитектуру книжного склада.

- 50+ классов (dataclass'ы и сервисы)
- 150+ полей (аннотированные атрибуты)
- 100+ уникальных поведений (методы)
- 30+ ассоциаций (поля/параметры методов с типами других доменных классов)
- 12 персональных исключений

## Структура
```
warehouse/
  exceptions.py
  models/
    core.py
    inventory.py
    finance.py
    orders.py
    comm.py
    filler.py
  services/
    auth_service.py
    inventory_service.py
    payment_service.py
main.py
verify.py
```
## Как запустить
```bash
python3 main.py
python3 verify.py
```
