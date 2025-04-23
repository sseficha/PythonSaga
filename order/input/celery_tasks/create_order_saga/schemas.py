from pydantic import BaseModel

from business.domains.order import Order


class ReserveStockReply(BaseModel):
    order: Order
    has_stock: bool


class FundCheckReply(BaseModel):
    order: Order
    has_funds: bool
