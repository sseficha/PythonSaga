from business.domains.order import Order
from input.celery_tasks.create_order_saga.orchestrator import CreateOrderSagaOrchestrator
from input.celery_tasks.create_order_saga.celery_adapter import CeleryAdapter
from input.celery_tasks.create_order_saga.orchestrator.states import SagaStep

from input.celery_tasks.create_order_saga.schemas import ReserveStockReply, FundCheckReply
from input.celery_tasks.main import app

from celery import chain, signature


@app.task(name=SagaStep.START.value, pydantic=True)
def start_create_order_saga(order: Order):
    orchestrator.start_create_order_saga(order)


@app.task(name=SagaStep.RESERVE_REPLY.value, pydantic=True)
def handle_reserve_stock_reply(reply: ReserveStockReply):
    orchestrator.handle_reserve_stock_reply(reply)


@app.task(name=SagaStep.FUND_REPLY.value, pydantic=True)
def handle_fund_check_reply(reply: FundCheckReply):
    orchestrator.handle_fund_check_reply(reply)


@app.task(name=SagaStep.APPROVE.value, pydantic=True)
def approve_order(order: Order):
    orchestrator.approve_order(order)


start_create_order_saga_signature = start_create_order_saga.s().set(queue="order_request_channel")

reserve_stock_chain = chain(
    signature("reserve_stock").set(queue="product_request_channel")
    | handle_reserve_stock_reply.s().set(queue="create_order_saga_reply_channel")
)

check_funds_chain = chain(
    signature("check_funds").set(queue="accounting_request_channel")
    | handle_fund_check_reply.s().set(queue="create_order_saga_reply_channel")
)

free_stock_signature = signature("free_stock").set(queue="product_request_channel")

approve_order_signature = approve_order.s().set(queue="order_request_channel")

celery_adapter = CeleryAdapter(
    start_saga=start_create_order_saga_signature,
    reserve_stock=reserve_stock_chain,
    check_funds=check_funds_chain,
    no_funds_compensate=free_stock_signature,
    approve_order=approve_order_signature,
)

orchestrator = CreateOrderSagaOrchestrator(celery_adapter)
