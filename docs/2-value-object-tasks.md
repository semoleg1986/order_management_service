# Руководство: Проектирование Value Object на примере OrderItem

Этот документ описывает логику проектирования объектов-значений (Value Objects) и их интеграцию в агрегаты.

---

## Шаг 1. Что такое Value Object (очень просто)

**Value Object** — это объект, который:
1.  **Не имеет собственной идентичности**: нам не важен его персональный ID, важны только данные, которые он несет.
2.  **Определяется только своими значениями**: две купюры по 100 рублей равны между собой.
3.  **Не живет отдельно от владельца**: он является частью более крупного целого.

**Примеры в жизни:**
* **Деньги**: (100₽ = 100₽).
* **Адрес**: (Улица, дом, город).
* **Строка чека**: «Товар × Количество × Цена».

---

## Шаг 2. Почему OrderItem — это Value Object

Для определения типа объекта мы используем логическую проверку:
* Есть ли у `OrderItem` свой уникальный ID в базе, который важен сам по себе? → ❌ **Нет**.
* Важен ли он системе в отрыве от заказа? → ❌ **Нет**.
* Может ли он существовать без родительского заказа? → ❌ **Нет**.



**Вывод:** `OrderItem` — это **Value Object**.

---

## Шаг 3. Состав и инварианты OrderItem

На «человеческом» языке объект описывает три факта:
* `product_id` — какой именно товар заказан.
* `quantity` — в каком количестве.
* `price` — цена за единицу **на момент оформления**.

> ⚠️ **Важно:** Цена копируется в заказ из каталога в момент добавления и больше не зависит от будущих изменений цены товара в магазине.

---

## Шаг 4. Реализация на Python

Мы используем `__slots__` для оптимизации памяти и свойства для защиты от случайного изменения полей.

```python
from uuid import UUID
from decimal import Decimal

class OrderItem:
    """
    ValueObject OrderItem
    - Неизменяем (immutability)
    - Сами валидирует свои данные (инварианты)
    - Не содержит бизнес-логику уровня сервисов
    """
    __slots__ = ('_product_id', '_quantity', '_price')

    def __init__(self, product_id: UUID, quantity: int, price: Decimal | str | float) -> None:
        # Валидация инвариантов
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        normalized_price = Decimal(str(price))

        if normalized_price <= Decimal("0"):
            raise ValueError("Price must be greater than zero")

        self._product_id = product_id
        self._quantity = quantity
        self._price = normalized_price

    @property
    def product_id(self) -> UUID: return self._product_id

    @property
    def quantity(self) -> int: return self._quantity

    @property
    def price(self) -> Decimal: return self._price

    def total_price(self) -> Decimal:
        return self.quantity * self.price

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderItem):
            return False
        return (self.product_id == other.product_id and
                self.quantity == other.quantity and
                self.price == other.price)

    def __hash__(self) -> int:
        return hash((self.product_id, self.quantity, self.price))
```
## Шаг 5. Поведение агрегата: управление объектами-значениями

Ключевой принцип **Агрегата** заключается в том, что он полностью контролирует свои части. Поскольку `OrderItem` неизменяем, мы не можем просто сказать `item.quantity = 5`. Мы должны заменить старый объект новым внутри списка агрегата.



### Реализация метода add_item
В этом методе реализуется бизнес-логика «слияния» (Merge): если товар с такой же ценой уже есть в заказе, мы суммируем количество.

```python
from decimal import Decimal
from uuid import UUID
from src.domain.value_object.order_item import OrderItem

class Order:
    ...
    def add_item(
            self,
            product_id: UUID,
            quantity: int,
            price: Decimal | str | float
    ) -> OrderItem:
        # Проверка инварианта: можно ли сейчас редактировать заказ?
        self._ensure_editable()

        normalized_price = Decimal(str(price))

        # 1. Пытаемся найти существующий товар для слияния
        for i, item in enumerate(self._items):
            if item.product_id == product_id and item.price == normalized_price:
                # ВАЖНО: Мы не меняем item.quantity, а создаем НОВЫЙ объект
                new_item = OrderItem(
                    product_id=product_id,
                    quantity=item.quantity + quantity,
                    price=normalized_price
                )
                self._items[i] = new_item
                self._touch() # Обновляем версию и время изменения заказа
                return new_item

        # 2. Если такого товара нет — создаем новую позицию
        new_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=normalized_price
        )

        self._items.append(new_item)
        self._touch()
        return new_item
```
## Шаг 6. Что мы получили (Итоги)

Реализовав этот подход, мы обеспечили:

*Целостность*: Нельзя создать позицию заказа с нулевой ценой.

*Безопасность*: Нельзя случайно изменить цену товара в уже существующем айтеме.

*Изоляцию*: Логика слияния товаров инкапсулирована внутри агрегата Order.