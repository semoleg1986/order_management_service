import pytest
from uuid import uuid4
from decimal import Decimal

from src.domain.entities.order import Order, OrderStatus
from src.domain.value_object.order_item import OrderItem

def test_create_order():
    order = Order()
    assert order.status == OrderStatus.NEW
    assert order.items == ()
    assert order._version == 1

def test_add_item_to_order():
    order = Order()
    product_id = uuid4()
    order_item = order.add_item(product_id=product_id, quantity=2, price="10.50")

    assert len(order.items) == 1
    assert order_item.product_id == product_id
    assert order_item.quantity == 2
    assert order_item.price == Decimal("10.50")

def test_add_item_merge_same_product_and_price():
    order = Order()
    product_id = uuid4()
    order.add_item(product_id=product_id, quantity=2, price="10.50")
    order.add_item(product_id=product_id, quantity=3, price=Decimal("10.50"))

    assert len(order.items) == 1
    item = order.items[0]
    assert item.quantity == 5
    assert item.price == Decimal("10.50")

def test_confirm_order():
    order = Order()
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert order._version == 2

def test_cannot_add_item_to_confirmed_order():
    order = Order()
    order.confirm()
    product_id = uuid4()
    with pytest.raises(ValueError):
        order.add_item(product_id=product_id, quantity=1, price="5.00")

def test_cancel_order():
    order = Order()
    order.cancel()
    assert order.status == OrderStatus.CANCELLED
    assert order._version == 2

def test_cannot_cancel_confirmed_order():
    order = Order()
    order.confirm()
    with pytest.raises(ValueError) as exc:
        order.cancel()
    assert str(exc.value) == "Confirmed order cannot be cancelled"