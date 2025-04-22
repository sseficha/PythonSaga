from fastapi import FastAPI

from business.domains.order import Order
from config import ORDER_DB_CONNECTION
from input.app.schemas.order import OrderIn
from input.celery_tasks.create_order_saga.tasks import (
    start_create_order_saga,
)
from output.utils import postgres_adapter_order_service

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/order")
def create_order(order_in: OrderIn) -> Order:
    order_items = [Order.OrderItem(**item.model_dump()) for item in order_in.items]
    order = Order(**{**order_in.model_dump(), **{"items": order_items}})
    with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
        order = order_service.create_order(order)
    start_create_order_saga.delay(order.model_dump())
    return order
