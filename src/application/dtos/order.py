from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class OrderItemDTO:
    """Вложенный DTO для элементов заказа"""

    product_id: UUID
    quantity: int
    price: Decimal
