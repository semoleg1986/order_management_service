from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum, auto
from uuid import UUID, uuid4

from src.domain.value_object.order_item import OrderItem


class OrderStatus(StrEnum):
    NEW = auto()
    CONFIRMED = auto()
    CANCELLED = auto()


class Order:
    """
    Aggregate Root: Order

    mermaid:
    classDiagram
        Order "1" *-- "many" OrderItem
        class Order {
            +UUID order_id
            +OrderStatus status
            +confirm()
            +cancel()
            +add_item()
        }
        class OrderItem {
            +UUID product_id
            +int quantity
            +Decimal price
            +total_price()
        }
    """

    __slots__ = (
        "_order_id",
        "_status",
        "_items",
        "_created_at",
        "_updated_at",
        "_version",
    )

    def __init__(
        self,
        order_id: UUID | None = None,
        items: list[OrderItem] | None = None,
        status: OrderStatus = OrderStatus.NEW,
        version: int = 1,
        created_at: datetime | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        self._order_id = order_id or uuid4()
        self._status = status
        self._items: list[OrderItem] = list(items) if items else []
        self._created_at = created_at or now
        self._updated_at = created_at or now
        self._version = version

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def items(self) -> tuple[OrderItem, ...]:
        return tuple(self._items)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def version(self) -> int:
        return self._version

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)
        self._version += 1

    def _ensure_editable(self) -> None:
        if self._status != OrderStatus.NEW:
            raise ValueError("Order cannot be modified in current state")

    def confirm(self) -> None:
        self._ensure_editable()
        if not self._items:
            raise ValueError("Cannot confirm an empty order")
        self._status = OrderStatus.CONFIRMED
        self._touch()

    def cancel(self) -> None:
        if self._status == OrderStatus.CONFIRMED:
            raise ValueError("Confirmed order cannot be cancelled")
        if self._status == OrderStatus.CANCELLED:
            return
        self._status = OrderStatus.CANCELLED
        self._touch()

    def total_price(self) -> Decimal:
        return sum((item.total_price() for item in self._items), Decimal("0"))

    def __repr__(self) -> str:
        return (
            f"Order("
            f"{self._order_id!r}, "
            f"status={self._status.value}, "
            f"version={self._version}, "
            f"created={self._created_at:%Y-%m-%d %H:%M:%S} "
            f"updated={self._updated_at:%Y-%m-%d %H:%M:%S})"
        )

    def __str__(self) -> str:
        return f"Order({self._order_id}, status={self._status.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self._order_id == other._order_id

    def __hash__(self) -> int:
        return hash(self._order_id)

    def add_item(
        self, product_id: UUID, quantity: int, price: Decimal | str | float
    ) -> OrderItem:
        self._ensure_editable()

        normalized_price = Decimal(str(price))

        for i, item in enumerate(self._items):
            if item.product_id == product_id and item.price == normalized_price:
                new_item = OrderItem(
                    product_id=product_id,
                    quantity=item.quantity + quantity,
                    price=normalized_price,
                )
                self._items[i] = new_item
                self._touch()
                return new_item

        new_item = OrderItem(
            product_id=product_id, quantity=quantity, price=normalized_price
        )

        self._items.append(new_item)
        self._touch()
        return new_item


if __name__ == "__main__":
    print("--- Smoke Test Started ---")

    # Создаем заказ
    order = Order()
    order_id = order.order_id

    # Проверяем хешируемость и коллекцию
    orders_registry = {order: "Active Order"}

    # Добавляем товар (Версия станет 2)
    order.add_item(uuid4(), 1, "100.50")

    # Меняем статус (Версия станет 3)
    order.confirm()

    # Проверяем, что заказ все еще находится в словаре по тому же ключу
    # (так как ID не изменился, а hash зависит только от него)
    status_in_dict = orders_registry.get(order)

    print(f"ID: {order_id}")
    print(f"Current Status: {order.status.value}")
    print(f"Version: {order.version}")
    print(f"Found in Registry: {status_in_dict is not None}")
    print(f"Representation: {repr(order)}")
    print("--- Smoke Test Finished ---")
