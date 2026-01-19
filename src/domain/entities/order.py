from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone


class OrderStatus(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Order:
    """
    Бизнес модель Order
    """
    __slots__ = ('order_id', '_status', '_created_at', '_updated_at', '_version')

    def __init__(self, order_id: UUID | None = None) -> None:
        now = datetime.now(timezone.utc)
        self.order_id = order_id or uuid4()
        self._status = OrderStatus.NEW
        self._created_at = now
        self._updated_at = now
        self._version = 1

    @property
    def status(self) -> OrderStatus:
        return self._status

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

if __name__ == "__main__":
    order1 = Order()
    order2 = Order(order1.order_id)
    order3 = Order()
    order3.confirm()
    print(order1==order2)
    print(order1==order3)

    my_set = {order1}
    my_set.add(order2)
    print(my_set)
    my_set.add(order3)
    print(my_set)
    print(order1._version)