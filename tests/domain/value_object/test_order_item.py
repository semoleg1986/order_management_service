import pytest
from uuid import uuid4
from decimal import Decimal
from src.domain.value_object.order_item import OrderItem

def test_order_item_creation():
    product_id = uuid4()
    quantity = 2
    price = Decimal("19.99")

    item = OrderItem(product_id, quantity, price)

    assert item.product_id == product_id
    assert item.quantity == quantity
    assert item.price == price

# ------------------------
# Инварианты
# ------------------------

def test_order_quantity_must_be_positive():
    with pytest.raises(ValueError) as excinfo:
        OrderItem(uuid4(), 0, Decimal("12.34"))
    assert "Quantity must be greater than zero" in str(excinfo.value)

def test_order_item_price_must_be_positive():
    with pytest.raises(ValueError) as excinfo:
        OrderItem(uuid4(), 1, Decimal("0"))
    assert "Price must be greater than zero" in str(excinfo.value)

# ------------------------
# Сравнение
# ------------------------

def test_order_item_equality():
    product_id = uuid4()
    item1 = OrderItem(product_id, 2, "10.00")
    item2 = OrderItem(product_id, 2, Decimal("10.00"))

    assert item1 == item2
    assert hash(item1) == hash(item2)