from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from src.domain.entities.order import Order


class OrderRepository(Protocol):
    async def get(self, order_id: UUID) -> Optional[Order]: ...

    async def save(self, order: Order) -> None: ...

    async def exists(self, order_id: UUID) -> bool: ...


