import logging

import psycopg
from celery import signature, chain
from pydantic import BaseModel

from business.domains.order import Order, OrderStates
from business.services.order_service import OrderService
from config import ORDER_DB_CONNECTION
from input.celery_tasks.create_order_saga.utils import check_saga_state
from input.celery_tasks.main import app
from output.order_repository import OrderRepository
from output.utils import postgres_adapter_order_service


@app.task(name="start_create_order_saga", pydantic=True)
def start_create_order_saga(order: Order):
    check_saga_state("start_create_order_saga", order.state)
    logging.info("Saga started")
    with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
        order = order_service.update_order_state(
            order.id, OrderStates.STOCK_RESERVATION_PENDING
        )
    reserve_stock_chain.delay(order.model_dump())


class ReserveStockReply(BaseModel):
    order: Order
    has_stock: bool


@app.task(name="handle_reserve_stock_reply", pydantic=True)
def handle_reserve_stock_reply(reply: ReserveStockReply):
    order = reply.order
    check_saga_state("handle_reserve_stock_reply", order.state)
    logging.info(f"Order {order} has stock: {reply.has_stock}")
    with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
        if reply.has_stock:
            order = order_service.update_order_state(
                order.id, OrderStates.FUND_CHECK_PENDING
            )
            check_funds_chain.delay(order.model_dump())
        else:
            order_service.update_order_state(
                order.id, OrderStates.STOCK_RESERVATION_FAILED
            )


class FundCheckReply(BaseModel):
    order: Order
    has_funds: bool


@app.task(name="handle_fund_check_reply", pydantic=True)
def handle_fund_check_reply(reply: FundCheckReply):
    order = reply.order
    check_saga_state("handle_fund_check_reply", order.state)
    logging.info(f"Order {order} has funds: {reply.has_funds}")
    with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
        if reply.has_funds:
            order_service.update_order_state(order.id, OrderStates.COMPLETED)
        else:
            order = order_service.update_order_state(
                order.id, OrderStates.FUND_CHECK_FAILED
            )
            check_funds_compensating_chain.delay(order.model_dump())


@app.task(name="cancel_order", pydantic=True)
def cancel_order(order: Order):
    check_saga_state("cancel_order", order.state)
    logging.info(f"Cancelling order {order}")
    with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
        order_service.update_order_state(order.id, OrderStates.CANCELED)


reserve_stock_chain = chain(
    signature("reserve_stock", queue="product_request_channel")
    | handle_reserve_stock_reply.s()
)

check_funds_chain = chain(
    signature("check_funds", queue="accounting_request_channel")
    | handle_fund_check_reply.s()
)

check_funds_compensating_chain = chain(
    signature("free_stock", queue="product_request_channel") | cancel_order.s()
)
