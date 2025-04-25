from typing import Optional

from business.domains.order import Order, OrderStates
from output.base_repository import BaseRepository


class OrderService:

    def __init__(self, repository: BaseRepository[Order]):
        self.repository = repository

    def create_order(self, order: Order) -> Order:
        order_id = self.repository.add(order)
        return self.repository.get_by_id(order_id)

    def update_order_state(self, order_id: int, state: OrderStates) -> Order:
        self.repository.update_state(order_id, state)
        return self.repository.get_by_id(order_id)

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        return self.repository.get_by_id(order_id)
