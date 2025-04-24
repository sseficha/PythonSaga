from fastapi import FastAPI

from business.domains.order import Order
from config import ORDER_DB_CONNECTION
from input.app.schemas.order import OrderIn
from input.celery_tasks.create_order_saga import (
    orchestrator as create_saga_orchestrator,
)
from output.utils import postgres_adapter_order_service

app = FastAPI()


@app.post("/order")
def create_order(order_in: OrderIn) -> Order:
    order_items = [Order.OrderItem(**item.model_dump()) for item in order_in.items]
    order = Order(**{**order_in.model_dump(), **{"items": order_items}})
    with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
        order = order_service.create_order(order)
    create_saga_orchestrator.initiate(order)
    return order
