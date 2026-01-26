from src.application.commands.cancel_order import CancelOrderCommand
from src.domain.exceptions.order_exception import OrderNotFoundError
from src.domain.repositories.order_repository import OrderRepository


class CancelOrderHandler:
    def __init__(self, order_repo: OrderRepository):
        self._order_repo = order_repo

    async def handle(self, cmd: CancelOrderCommand) -> None:
        order = await self._order_repo.get(cmd.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {cmd.order_id} not found")

        order.cancel()

        await self._order_repo.save(order)
