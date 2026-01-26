from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.order import OrderItemDTO


@dataclass(frozen=True)
class AddOrderItemCommand:
    order_id: UUID
    item: OrderItemDTO
