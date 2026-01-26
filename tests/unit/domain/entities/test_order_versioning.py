from uuid import uuid4

from src.domain.entities.order import Order


def test_order_version_increments_on_every_change():
    order = Order()
    initial_version = order.version

    order.add_item(uuid4(), 1, "10.00")
    assert order.version == initial_version + 1

    order.confirm()
    assert order.version == initial_version + 2
