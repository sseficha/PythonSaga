from functools import partial

from business.domains.order import Order
from input.celery_tasks.create_order_saga.orchestrator import (
    CreateOrderSagaOrchestrator,
)

from input.celery_tasks.create_order_saga.schemas import (
    ReserveStockReply,
    FundCheckReply,
)
from input.celery_tasks.main import app

from celery import chain, signature


@app.task(name="start_create_order_saga", pydantic=True, queue="order_request_channel")
def start_create_order_saga(order: Order):
    orchestrator.start_create_order_saga(order)


@app.task(
    name="handle_reserve_stock_reply",
    pydantic=True,
    queue="create_order_saga_reply_channel",
)
def handle_reserve_stock_reply(reply: ReserveStockReply):
    orchestrator.handle_reserve_stock_reply(reply)


@app.task(
    name="handle_fund_check_reply",
    pydantic=True,
    queue="create_order_saga_reply_channel",
)
def handle_fund_check_reply(reply: FundCheckReply):
    orchestrator.handle_fund_check_reply(reply)


@app.task(name="approve_order", pydantic=True, queue="order_request_channel")
def approve_order(order: Order):
    orchestrator.approve_order(order)


reserve_stock_chain = chain(
    signature(
        "reserve_stock",
    ).set(queue="product_request_channel")
    | handle_reserve_stock_reply.s().set(queue="create_order_saga_reply_channel")
)

check_funds_chain = chain(
    signature(
        "check_funds",
    ).set(queue="accounting_request_channel")
    | handle_fund_check_reply.s().set(queue="create_order_saga_reply_channel")
)

no_funds_compensating_chain = chain(
    signature(
        "free_stock",
    ).set(queue="product_request_channel")
)

approve_order_chain = chain(approve_order.s().set(queue="order_request_channel"))

orchestrator = CreateOrderSagaOrchestrator(
    start_saga=partial(start_create_order_saga.delay),
    reserve_stock=partial(reserve_stock_chain.delay),
    check_funds=partial(check_funds_chain.delay),
    no_funds_compensate=partial(no_funds_compensating_chain.delay),
    approve_order=partial(approve_order_chain.delay),
)
