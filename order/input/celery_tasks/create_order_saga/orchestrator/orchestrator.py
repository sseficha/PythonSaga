import logging
import os

from business.domains.order import Order, OrderStates
from input.celery_tasks.create_order_saga.celery_adapter import CeleryAdapter

from input.celery_tasks.create_order_saga.orchestrator.exceptions import InvalidSagaStateError

from input.celery_tasks.create_order_saga.orchestrator.states import ALLOWED_STATE_MAP, SagaStep
from input.celery_tasks.create_order_saga.schemas import ReserveStockReply, FundCheckReply
from output.utils import order_service_postgres_context


class CreateOrderSagaOrchestrator:

    def __init__(self, celery_adapter: CeleryAdapter):
        self.celery_adapter = celery_adapter

    def initiate(self, order: Order):
        self.check_saga_state(SagaStep.START, order.state)
        logging.info("Saga started")
        with order_service_postgres_context(os.environ["ORDER_DB_CONNECTION"]) as order_service:
            order = order_service.update_order_state(order.id, OrderStates.STOCK_RESERVATION_PENDING)
        self.celery_adapter.reserve_stock(order)

    @staticmethod
    def check_saga_state(step: SagaStep, state: OrderStates):
        try:
            if state not in ALLOWED_STATE_MAP[step]:
                raise InvalidSagaStateError(step, state)
        except KeyError:
            raise ValueError(f"Invalid step name: {step}")

    def handle_reserve_stock_reply(self, reply: ReserveStockReply):
        order = reply.order
        self.check_saga_state(SagaStep.RESERVE_REPLY, order.state)
        logging.info(f"Order {order} has stock: {reply.has_stock}")
        with order_service_postgres_context(os.environ["ORDER_DB_CONNECTION"]) as order_service:
            if reply.has_stock:
                order = order_service.update_order_state(order.id, OrderStates.FUND_CHECK_PENDING)
            else:
                order_service.update_order_state(order.id, OrderStates.STOCK_RESERVATION_FAILED)
        if reply.has_stock:
            self.celery_adapter.check_funds(order)

    def handle_fund_check_reply(self, reply: FundCheckReply):
        order = reply.order
        self.check_saga_state(SagaStep.FUND_REPLY, order.state)
        logging.info(f"Order {order} has funds: {reply.has_funds}")
        with order_service_postgres_context(os.environ["ORDER_DB_CONNECTION"]) as order_service:
            if reply.has_funds:
                order = order_service.update_order_state(order.id, OrderStates.FUND_CHECK_SUCCEEDED)
            else:
                order = order_service.update_order_state(order.id, OrderStates.FUND_CHECK_FAILED)
        if reply.has_funds:
            self.celery_adapter.approve_order(order)
        else:
            self.celery_adapter.no_funds_compensate(order)

    def approve_order(self, order: Order):
        self.check_saga_state(SagaStep.APPROVE, order.state)
        logging.info(f"Approving order {order}")
        with order_service_postgres_context(os.environ["ORDER_DB_CONNECTION"]) as order_service:
            order_service.update_order_state(order.id, OrderStates.COMPLETED)
