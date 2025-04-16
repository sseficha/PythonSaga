import psycopg
from fastapi import FastAPI

from business.domains.order import Order
from business.services.order_service import OrderService
from input.app.schemas.order import OrderIn
from input.celery_tasks.create_order_saga.tasks import create_order_saga_chain
from output.order_repository import OrderRepository

app = FastAPI()

ORDER_DB_CONNECTION = "postgresql://postgres:postgres@order-db/order_db"


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/order")
def create_order(order_in: OrderIn):
    order = Order(**order_in.model_dump())
    with psycopg.connect(ORDER_DB_CONNECTION) as conn:
        order_repository = OrderRepository(conn)
        order_service = OrderService(order_repository)
        order_service.create_order(order)
    create_order_saga_chain.delay(order.model_dump())
    return {"order_id": order.id}
