import logging

from business.domains.order import Order, OrderStates
from business.services.order_service import OrderService
from input.celery_tasks.create_order_saga.celery_adapter import CeleryAdapter

from input.celery_tasks.create_order_saga.orchestrator.exceptions import InvalidSagaStateError, OrderNotFoundError

from input.celery_tasks.create_order_saga.orchestrator.states import ALLOWED_STATES_FOR_STEP, SagaStep
from input.celery_tasks.create_order_saga.schemas import ReserveStockReply, FundCheckReply

from output.postgres_order_repository import PostgresOrderRepository


class CreateOrderSagaOrchestrator:

    def __init__(self, celery_adapter: CeleryAdapter):
        self.celery_adapter = celery_adapter

    def initiate(self, order: Order):
        self.check_saga_state(SagaStep.START, order.state)
        logging.info("Saga started")
        order = OrderService(PostgresOrderRepository).update_order_state(
            order.id, OrderStates.STOCK_RESERVATION_PENDING
        )
        self.celery_adapter.reserve_stock(order)

    @staticmethod
    def check_saga_state(step: SagaStep, state: OrderStates):
        try:
            if state not in ALLOWED_STATES_FOR_STEP[step]:
                raise InvalidSagaStateError(step, state)
        except KeyError:
            raise ValueError(f"Invalid step name: {step}")

    def handle_reserve_stock_reply(self, reply: ReserveStockReply):
        order_service = OrderService(PostgresOrderRepository)
        order = order_service.get_order_by_id(reply.order_id)
        if order is None:
            raise OrderNotFoundError(reply.order_id)
        self.check_saga_state(SagaStep.RESERVE_REPLY, order.state)
        if reply.has_stock:
            order = order_service.update_order_state(order.id, OrderStates.FUND_CHECK_PENDING)
        else:
            order_service.update_order_state(order.id, OrderStates.STOCK_RESERVATION_FAILED)
        if reply.has_stock:
            self.celery_adapter.check_funds(order)

    def handle_fund_check_reply(self, reply: FundCheckReply):
        order_service = OrderService(PostgresOrderRepository)
        order = order_service.get_order_by_id(reply.order_id)
        if order is None:
            raise OrderNotFoundError(reply.order_id)
        self.check_saga_state(SagaStep.FUND_REPLY, order.state)
        if reply.has_funds:
            order = order_service.update_order_state(order.id, OrderStates.FUND_CHECK_SUCCEEDED)
        else:
            order = order_service.update_order_state(order.id, OrderStates.FUND_CHECK_FAILED)
        if reply.has_funds:
            self.celery_adapter.approve_order(order)
        else:
            self.celery_adapter.no_funds_compensate(order)

    def approve_order(self, order_id: int):
        order_service = OrderService(PostgresOrderRepository)
        order = order_service.get_order_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        self.check_saga_state(SagaStep.APPROVE, order.state)
        order_service.update_order_state(order.id, OrderStates.COMPLETED)
