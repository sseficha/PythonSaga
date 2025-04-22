from enum import Enum

from business.domains.order import OrderStates


class InvalidSagaStateError(Exception):
    def __init__(self, step_name: str, state: Enum):
        super().__init__(
            f"Invalid state: {state} when executing saga step: {step_name}"
        )


def check_saga_state(step: str, state: Enum):
    allowed_state_map = {
        "start_create_order_saga": [OrderStates.PENDING],
        "handle_reserve_stock_reply": [OrderStates.STOCK_RESERVATION_PENDING],
        "handle_fund_check_reply": [OrderStates.FUND_CHECK_PENDING],
        "cancel_order": [
            OrderStates.PENDING,
            OrderStates.STOCK_RESERVATION_FAILED,
            OrderStates.FUND_CHECK_FAILED,
        ],
        "approve_order": [OrderStates.FUND_CHECK_SUCCEEDED],
    }
    try:
        if state not in allowed_state_map[step]:
            raise InvalidSagaStateError(step, state)
    except KeyError:
        raise ValueError(f"Invalid step name: {step}")
