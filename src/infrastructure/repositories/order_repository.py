from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from src.domain.repositories.order_repository import OrderRepository

if TYPE_CHECKING:
    from src.domain.entities.order import Order


class OrderRepositoryMemory(OrderRepository):
    def __init__(self):
        self._storage: dict[UUID, Order] = {}

    async def get(self, order_id: UUID) -> Optional[Order]:
        order = self._storage.get(order_id)

        if order is None:
            return None
        return copy.deepcopy(order)

    async def save(self, order: Order) -> None:
        self._storage[order.order_id] = copy.deepcopy(order)

    async def exists(self, order_id: UUID) -> bool:
        return order_id in self._storage
