from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.application.dtos.order import OrderItemDTO


@dataclass(frozen=True)
class CreateOrderCommand:
    """
    Команда на создание заказа.
    Использует примитивы или простые DTO, чтобы не зависеть от домена.
    """

    # Мы можем позволить клиенту передать свой ID или генерируем его сами
    order_id: UUID = field(default_factory=uuid4)
    items: list[OrderItemDTO] = field(default_factory=list)
