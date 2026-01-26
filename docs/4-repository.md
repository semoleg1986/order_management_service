# Репозиторий (очень аккуратно)

Важно:
мы не пишем базу данных,
мы не пишем SQL,
мы учимся отделять домен от хранения.

## Шаг 3. Зачем вообще нужен репозиторий

Проблема:
Order — чистый доменный объект

Но его нужно:
- сохранить
- загрузить

*Order не должен знать КАК это делается.*

Решение DDD:

_Репозиторий — это «коллекция агрегатов»._

## Шаг 4. Интерфейс репозитория (в домене)

```python
from typing import Protocol, Optional
from uuid import UUID

from src.domain.entities.order import Order


class OrderRepository(Protocol):
    def get(self, order_id: UUID) -> Optional[Order]:
        ...
    
    def save(self, order: Order) -> None:
        ...
```

🔴 Ключевые моменты:
- это интерфейс
-  БД
- инфраструктуры
- домен ни от чего не зависит

## Шаг 5. In-Memory реализация (для обучения)

```python
from typing import TYPE_CHECKING
from uuid import UUID


if TYPE_CHECKING:
    from src.domain.entities.order import Order
    
class InMemoryOrderRepository:
    def __init__(self):
        self._storage: dict[UUID, Order] = {}

    def get(self, order_id: UUID) -> Order | None:
        return self._storage.get(order_id)

    def save(self, order: Order) -> None:
        self._storage[order.id] = order
```
Это не домен, это инфраструктура.

## Шаг 6. Кто теперь управляет сценарием?

Ответ: Application Service

Он:
- получает команду
- загружает агрегат
- вызывает его методы
- сохраняет результат

### Минимальный application-сервис

```python
class OrderService:
    def __init__(self, repository: OrderRepository):
        self._repository = repository

    def create_order(self) -> UUID:
        order = Order()
        self._repository.save(order)
        return order.id

    def add_item(
        self,
        order_id: UUID,
        product_id: UUID,
        quantity: int,
        price: float,
    ) -> None:
        order = self._repository.get(order_id)
        if order is None:
            raise ValueError("Order not found")

        order.add_item(product_id, quantity, price)
        self._repository.save(order)
```

⚠️ Обрати внимание:
- нет бизнес-логики
- всё в агрегате
- сервис — только оркестрация

- что такое Aggregate Root
- зачем нужны репозитории
- чем домен отличается от application layer
- почему сервисы не содержат бизнес-логики