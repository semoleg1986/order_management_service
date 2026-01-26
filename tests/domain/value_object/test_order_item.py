from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.value_object.order_item import OrderItem

# --- Группа 1: Валидация при создании (Инварианты) ---


def test_order_item_creation():
    product_id = uuid4()
    quantity = 2
    price = Decimal("19.99")

    item = OrderItem(product_id, quantity, price)

    assert item.product_id == product_id
    assert item.quantity == quantity
    assert item.price == price


def test_order_quantity_must_be_positive():
    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        OrderItem(uuid4(), 0, Decimal("12.34"))

    with pytest.raises(ValueError, match="Quantity must be greater than zero"):
        OrderItem(uuid4(), -1, Decimal("12.34"))


def test_order_item_price_must_be_positive():
    with pytest.raises(ValueError, match="Price must be greater than zero"):
        OrderItem(uuid4(), 1, Decimal("0"))

    with pytest.raises(ValueError, match="Price must be greater than zero"):
        OrderItem(uuid4(), 1, Decimal("-1.00"))


# --- Группа 2: Поведение Value Object (Equality & Immutability) ---


def test_order_item_equality():
    product_id = uuid4()
    # Проверяем, что разные типы (str и Decimal) приводятся к общему знаменателю,
    # если ваш Order.add_item это делает, или просто сравниваем идентичные объекты
    item1 = OrderItem(product_id, 2, Decimal("10.00"))
    item2 = OrderItem(product_id, 2, Decimal("10.00"))
    item3 = OrderItem(product_id, 5, Decimal("10.00"))  # Другое количество

    assert item1 == item2
    assert hash(item1) == hash(item2)
    assert item1 != item3  # Разные значения — разные объекты


def test_order_item_is_immutable():
    """Проверяем, что frozen=True работает"""
    item = OrderItem(uuid4(), 1, Decimal("10.00"))

    with pytest.raises(AttributeError):
        item.quantity = 10


# --- Группа 3: Работа с Decimal ---


def test_order_item_price_precision():
    """Проверка, что точность Decimal сохраняется"""
    price = Decimal("10.123456789")
    item = OrderItem(uuid4(), 1, price)
    assert item.price == price


# --- Группа 4: Расчеты ---


def test_order_item_total_price():
    """Проверка базового расчета стоимости позиции (цена * количество)."""
    item = OrderItem(product_id=uuid4(), quantity=3, price=Decimal("150.50"))
    # 3 * 150.50 = 451.50
    assert item.total_price() == Decimal("451.50")


def test_order_item_total_price_precision():
    """Проверка точности при умножении дробных чисел."""
    item = OrderItem(product_id=uuid4(), quantity=2, price=Decimal("10.1234"))
    # 2 * 10.1234 = 20.2468
    assert item.total_price() == Decimal("20.2468")


def test_order_item_total_price_with_large_quantity():
    """Проверка расчета при больших объемах (целочисленное переполнение и т.д.)."""
    item = OrderItem(product_id=uuid4(), quantity=1_000_000, price=Decimal("0.01"))
    assert item.total_price() == Decimal("10000.00")
