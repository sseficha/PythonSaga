from business.domains.order import Order, OrderStates
from output.order_repository import OrderRepository


class OrderService:

    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, order: Order) -> int:
        self.repository.add(order)
        return order.id

    def update_order_state(self, order_id: int, state: OrderStates):
        self.repository.update_state(order_id, state)
