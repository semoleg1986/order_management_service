from enum import Enum
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timezone

from src.domain.value_object.order_item import OrderItem


class OrderStatus(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Order:
    """
    Бизнес модель Order
    """
    __slots__ = ('order_id', '_status', '_items','_created_at', '_updated_at', '_version')

    def __init__(self, order_id: UUID | None = None, items: list[OrderItem] | None = None) -> None:
        now = datetime.now(timezone.utc)
        self.order_id = order_id or uuid4()
        self._status = OrderStatus.NEW
        self._items: list[OrderItem] = items or []
        self._created_at = now
        self._updated_at = now
        self._version = 1

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

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)
        self._version += 1

    def confirm(self) -> None:
        if self._status != OrderStatus.NEW:
            raise ValueError("Only new orders can be confirmed")
        self._status = OrderStatus.CONFIRMED
        self._touch()

    def cancel(self) -> None:
        if self._status == OrderStatus.CONFIRMED:
            raise ValueError("Confirmed order cannot be cancelled")
        if self._status == OrderStatus.CANCELLED:
            return
        self._status = OrderStatus.CANCELLED
        self._touch()

    def __repr__(self) -> str:
        return (
            f"Order("
            f"{self.order_id!r}, "
            f"status={self._status.value!r}), "
            f"version={self._version}, "
            f"created={self._created_at:%Y-%m-%d %H:%M:%S} "
            f"updated={self._updated_at:%Y-%m-%d %H:%M:%S} "
            f")"
        )

    def __str__(self) -> str:
        return f"Order({self.order_id}, status={self._status.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self) -> int:
        return hash(self.order_id)

    def add_item(
            self,
            product_id: UUID,
            quantity: int,
            price: Decimal | str | float
    ) -> OrderItem:
        if self.status != OrderStatus.NEW:
            raise ValueError("Cannot modify confirmed or cancelled order")

        normalized_price = Decimal(str(price))

        for i, item in enumerate(self._items):
            if item.product_id == product_id and item.price == normalized_price:
                new_item = OrderItem(
                    product_id=product_id,
                    quantity=item.quantity + quantity,
                    price=normalized_price
                )
                self._items[i] = new_item
                self._touch()
                return new_item

        new_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=normalized_price
        )

        self._items.append(new_item)
        self._touch()
        return new_item
