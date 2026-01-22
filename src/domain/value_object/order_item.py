from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True, slots=True)
class OrderItem:
    """
    ValueObject OrderItem
    •	нет сеттеров
	•	нет анемичной модели
	•	нет логики в сервисах
    """
    product_id: UUID
    quantity: int
    price: Decimal

    def total_price(self) -> Decimal:
        return self.quantity * self.price

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        try:
            normalized_price = Decimal(str(self.price))
        except (InvalidOperation, TypeError):
            raise ValueError("Invalid price value")

        if normalized_price <= Decimal("0"):
            raise ValueError("Price must be greater than zero")

        object.__setattr__(self, "price", normalized_price)


    # __slots__ = ('_product_id', '_quantity', '_price')
    #
    # def __init__(self, product_id: UUID, quantity: int, price: Decimal | str | float) -> None:
    #     if quantity <= 0:
    #         raise ValueError("Quantity must be greater than zero")
    #
    #     normalized_price = Decimal(str(price))
    #
    #     if normalized_price <= Decimal("0"):
    #         raise ValueError("Price must be greater than zero")
    #
    #     self._product_id = product_id
    #     self._quantity = quantity
    #     self._price = normalized_price
    #
    # @property
    # def product_id(self) -> UUID:
    #     return self._product_id
    #
    # @property
    # def quantity(self) -> int:
    #     return self._quantity
    #
    # @property
    # def price(self) -> Decimal:
    #     return self._price
    #
    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, OrderItem):
    #         return False
    #     return (
    #         self.product_id == other.product_id
    #         and self.quantity == other.quantity
    #         and self.price == other.price
    #     )
    #
    # def __repr__(self) -> str:
    #     return (f"OrderItem({self.product_id!r}, "
    #             f"qty={self.quantity}, "
    #             f"price={self.price})")
    #
    # def __str__(self) -> str:
    #     return (f"OrderItem({self.product_id}, "
    #             f"qty={self.quantity}, "
    #             f"price={self.price})")
    #
    # def __hash__(self) -> int:
    #     return hash((self.product_id, self.quantity, self.price))