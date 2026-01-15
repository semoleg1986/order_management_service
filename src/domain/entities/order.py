from enum import Enum
from uuid import UUID, uuid4

class OrderStatus(Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Order:
    """
    Бизнес модель Order
    """
    __slots__ = ('order_id', '_status')

    def __init__(self, order_id: UUID | None = None) -> None:
        self.order_id = order_id or uuid4()
        self._status = OrderStatus.NEW

    @property
    def status(self) -> OrderStatus:
        return self._status

    def confirm(self) -> None:
        if self._status != OrderStatus.NEW:
            raise ValueError("Only new orders can be confirmed")
        self._status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self._status == OrderStatus.CONFIRMED:
            raise ValueError("Confirmed order cannot be cancelled")
        if self._status == OrderStatus.CANCELLED:
            raise ValueError("Canceled order cannot be cancelled")
        self._status = OrderStatus.CANCELLED

    def __repr__(self) -> str:
        return f"Order({self.order_id!r}, status={self._status.value})"

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