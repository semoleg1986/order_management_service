import copy
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from src.domain.repositories.order_repository import OrderRepository

if TYPE_CHECKING:
    from src.domain.entities.order import Order


class OrderRepositoryMemory(OrderRepository):
    def __init__(self):
        self._storage: dict[UUID, "Order"] = {}

    async def get(self, order_id: UUID) -> Optional["Order"]:
        return self._storage.get(order_id)

    async def save(self, order: "Order") -> None:
        self._storage[order.order_id] = copy.deepcopy(order)

    async def exists(self, order_id: UUID) -> bool:
        return order_id in self._storage
