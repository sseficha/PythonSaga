from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class OrderStates(StrEnum):
    STOCK_RESERVATION_PENDING = "stock_reservation_pending"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


class Order(BaseModel):
    id: int | None
    created_at: datetime | None
    state: OrderStates
    user_id: int
    items: list[dict]

    def __init__(self, **kwargs):
        super().__init__(
            id=kwargs.get("id"),
            created_at=kwargs.get("created_at"),
            state=kwargs.get("state", OrderStates.PENDING),
            user_id=kwargs.get("user_id"),
            items=kwargs.get("items"),
        )

        if not self.reaches_order_minimum():
            raise ValueError("Order does not meet the minimum amount")

    def reaches_order_minimum(self) -> bool:
        return (
            sum(item["price_per_unit"] * item["quantity"] for item in self.items) >= 10
        )
