from decimal import Decimal
from uuid import uuid4

import pytest

from src.application.commands.add_order_item import AddOrderItemCommand, OrderItemDTO
from src.application.commands.create_order import CreateOrderCommand
from src.application.handlers.add_item import AddOrderItemHandler
from src.application.handlers.create_order import CreateOrderHandler
from src.domain.entities.order import Order
from src.infrastructure.repositories.order_repository import OrderRepositoryMemory


@pytest.mark.asyncio
async def test_order_full_lifecycle_smoke():
    # 1. Setup (Инфраструктура)
    repo = OrderRepositoryMemory()
    create_handler = CreateOrderHandler(repo)
    add_item_handler = AddOrderItemHandler(repo)

    order_id = uuid4()

    # 2. Создание заказа
    await create_handler.handle(CreateOrderCommand(order_id=order_id))

    # 3. Добавление товара
    item_dto = OrderItemDTO(product_id=uuid4(), quantity=2, price=Decimal("100.00"))
    await add_item_handler.handle(AddOrderItemCommand(order_id=order_id, item=item_dto))

    # 4. Проверка результата
    order = await repo.get(order_id)
    assert order is not None
    assert len(order.items) == 1
    assert order.total_price() == Decimal("200.00")
    assert order.version > 1


@pytest.mark.asyncio
async def test_repository_isolation():
    repo = OrderRepositoryMemory()
    order = Order(order_id=uuid4())
    await repo.save(order)

    # Достаем объект и меняем его
    retrieved_order = await repo.get(order.order_id)
    retrieved_order.add_item(uuid4(), 1, Decimal("100"))

    # Снова достаем из репозитория — там должен быть оригинал без товара!
    fresh_order = await repo.get(order.order_id)
    assert len(fresh_order.items) == 0
