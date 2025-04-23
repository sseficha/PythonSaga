import logging
from typing import Callable

from business.domains.order import Order, OrderStates
from config import ORDER_DB_CONNECTION


from input.celery_tasks.create_order_saga.orchestrator.exceptions import (
    InvalidSagaStateError,
)

from input.celery_tasks.create_order_saga.orchestrator.states import ALLOWED_STATE_MAP
from input.celery_tasks.create_order_saga.schemas import (
    ReserveStockReply,
    FundCheckReply,
)
from output.utils import postgres_adapter_order_service


class CreateOrderSagaOrchestrator:

    def __init__(
        self,
        reserve_stock: Callable,
        check_funds: Callable,
        no_funds_compensate: Callable,
        approve_order: Callable,
    ):
        self.reserve_stock = reserve_stock
        self.check_funds = check_funds
        self.no_funds_compensate = no_funds_compensate
        self.approve_order = approve_order

    @staticmethod
    def check_saga_state(step: str, state: OrderStates):
        try:
            if state not in ALLOWED_STATE_MAP[step]:
                raise InvalidSagaStateError(step, state)
        except KeyError:
            raise ValueError(f"Invalid step name: {step}")

    def start_create_order_saga(self, order: Order):
        self.check_saga_state("start_create_order_saga", order.state)
        logging.info("Saga started")
        with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
            order = order_service.update_order_state(
                order.id, OrderStates.STOCK_RESERVATION_PENDING
            )
        self.reserve_stock(order.model_dump())

    def handle_reserve_stock_reply(self, reply: ReserveStockReply):
        order = reply.order
        self.check_saga_state("handle_reserve_stock_reply", order.state)
        logging.info(f"Order {order} has stock: {reply.has_stock}")
        with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
            if reply.has_stock:
                order = order_service.update_order_state(
                    order.id, OrderStates.FUND_CHECK_PENDING
                )
                self.check_funds(order.model_dump())
            else:
                order_service.update_order_state(
                    order.id, OrderStates.STOCK_RESERVATION_FAILED
                )

    def handle_fund_check_reply(self, reply: FundCheckReply):
        order = reply.order
        self.check_saga_state("handle_fund_check_reply", order.state)
        logging.info(f"Order {order} has funds: {reply.has_funds}")
        with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
            if reply.has_funds:
                order = order_service.update_order_state(
                    order.id, OrderStates.FUND_CHECK_SUCCEEDED
                )
                self.approve_order(order.model_dump())
            else:
                order = order_service.update_order_state(
                    order.id, OrderStates.FUND_CHECK_FAILED
                )
                self.no_funds_compensate(order.model_dump())

    def approve_order(self, order: Order):
        self.check_saga_state("approve_order", order.state)
        logging.info(f"Approving order {order}")
        with postgres_adapter_order_service(ORDER_DB_CONNECTION) as order_service:
            order_service.update_order_state(order.id, OrderStates.COMPLETED)
