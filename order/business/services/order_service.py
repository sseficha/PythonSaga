from typing import Optional, Type

from business.domains.order import Order, OrderStates
from output.base_repository import BaseRepository


class OrderService:

    def __init__(self, repository: Type[BaseRepository[Order]]):
        self.repository = repository

    def create_order(self, order: Order) -> Order:
        with self.repository.connect() as repo:
            order_id = repo.add(order)
            return repo.get_by_id(order_id)

    def update_order_state(self, order_id: int, state: OrderStates) -> Order:
        with self.repository.connect() as repo:
            repo.update_state(order_id, state)
            return repo.get_by_id(order_id)

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        with self.repository.connect() as repo:
            return repo.get_by_id(order_id)
