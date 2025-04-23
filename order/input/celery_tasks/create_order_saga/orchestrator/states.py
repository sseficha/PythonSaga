from business.domains.order import OrderStates

ALLOWED_STATE_MAP = {
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
