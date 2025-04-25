from business.domains.order import OrderStates

from enum import Enum


class SagaStep(str, Enum):
    START = "start_create_order_saga"
    RESERVE_REPLY = "handle_reserve_stock_reply"
    FUND_REPLY = "handle_fund_check_reply"
    APPROVE = "approve_order"


ALLOWED_STATES_FOR_STEP = {
    SagaStep.START: [OrderStates.PENDING],
    SagaStep.RESERVE_REPLY: [OrderStates.STOCK_RESERVATION_PENDING],
    SagaStep.FUND_REPLY: [OrderStates.FUND_CHECK_PENDING],
    SagaStep.APPROVE: [OrderStates.FUND_CHECK_SUCCEEDED],
}
