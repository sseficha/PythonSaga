from pydantic import BaseModel

from business.domains.order import Order


class ReserveStockReply(BaseModel):
    order_id: int
    has_stock: bool


class FundCheckReply(BaseModel):
    order_id: int
    has_funds: bool
