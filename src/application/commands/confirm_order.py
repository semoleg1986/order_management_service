from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ConfirmOrderCommand:
    order_id: UUID
