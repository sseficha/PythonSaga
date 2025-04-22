from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class OrderStates(StrEnum):
    STOCK_RESERVATION_PENDING = "stock_reservation_pending"
    STOCK_RESERVATION_FAILED = "stock_reservation_failed"
    FUND_CHECK_PENDING = "fund_check_pending"
    FUND_CHECK_FAILED = "fund_check_failed"
    COMPLETED = "completed"
    CANCELED = "canceled"
    PENDING = "pending"


class Order(BaseModel):

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    state: OrderStates = OrderStates.PENDING
    user_id: int

    class Config:
        arbitrary_types_allowed = True

    class OrderItem(BaseModel):
        id: Optional[int] = None
        item_id: int
        quantity: int
        price_per_unit: float

    items: list[OrderItem]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.reaches_order_minimum():
            raise ValueError("Order does not meet the minimum amount")

    def reaches_order_minimum(self) -> bool:
        return sum(item.price_per_unit * item.quantity for item in self.items) >= 10
