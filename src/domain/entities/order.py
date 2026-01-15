from uuid import UUID, uuid4

class Order:
    """
    Бизнес модель Order
    """
    __slots__ = ('order_id',)

    def __init__(self, order_id: UUID | None = None) -> None:
        self.order_id = order_id or uuid4()