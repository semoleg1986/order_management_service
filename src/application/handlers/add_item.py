from src.application.commands.add_order_item import AddOrderItemCommand
from src.domain.repositories.order_repository import OrderRepository


class AddOrderItemHandler:
    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    async def handle(self, cmd: AddOrderItemCommand) -> None:
        order = await self._order_repo.get(cmd.order_id)
        if not order:
            raise ValueError("Заказ не найден")

        order.add_item(
            product_id=cmd.item.product_id,
            quantity=cmd.item.quantity,
            price=cmd.item.price,
        )

        await self._order_repo.save(order)
