from uuid import UUID

from src.application.commands.create_order import CreateOrderCommand
from src.domain.entities.order import Order
from src.domain.exceptions.order_exception import OrderAlreadyExistsError
from src.domain.repositories.order_repository import OrderRepository


class CreateOrderHandler:
    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    async def handle(self, cmd: CreateOrderCommand) -> UUID:
        if await self._order_repo.exists(cmd.order_id):
            raise OrderAlreadyExistsError(f"Order {cmd.order_id} already exists")

        new_order = Order(order_id=cmd.order_id)

        for item in cmd.items:
            new_order.add_item(
                product_id=item.product_id, quantity=item.quantity, price=item.price
            )

        await self._order_repo.save(new_order)

        return new_order.order_id
