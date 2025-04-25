from business.domains.order import OrderStates


class InvalidSagaStateError(Exception):
    def __init__(self, step_name: str, state: OrderStates):
        super().__init__(f"Invalid state: {state} when executing saga step: {step_name}")


class OrderNotFoundError(Exception):
    def __init__(self, order_id: int):
        super().__init__(f"Order with ID {order_id} not found.")
