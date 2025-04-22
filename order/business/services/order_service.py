from business.domains.order import Order, OrderStates
from output.order_repository import OrderRepository


class OrderService:

    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, order: Order) -> Order:
        order_id = self.repository.add(order)
        return self.repository.get_by_id(order_id)

    def update_order_state(self, order_id: int, state: OrderStates) -> Order:
        self.repository.update_state(order_id, state)
        return self.repository.get_by_id(order_id)
