from typing import Optional

from business.domains.order import Order, OrderStates
from output.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, connection):
        self.connection = connection

    def add(self, order: Order):
        with self.connection.cursor() as cursor:
            order_id, created_at = cursor.execute(
                "INSERT INTO orders (user_id, state) VALUES (%(user_id)s, %(state)s) RETURNING id, created_at",
                {"user_id": order.user_id, "state": order.state},
            ).fetchone()

            for item in order.items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity, price_per_unit) VALUES "
                    "(%(order_id)s, %(item_id)s, %(quantity)s, %(price_per_unit)s)",
                    {
                        "order_id": order_id,
                        "item_id": item["item_id"],
                        "quantity": item["quantity"],
                        "price_per_unit": item["price_per_unit"],
                    },
                )
        order.id = order_id
        order.created_at = created_at

    def get_by_id(self, order_id: int) -> Optional[Order]:
        pass
        # cursor = self.connection.cursor()
        # cursor.execute("SELECT id, name, age FROM persons WHERE id=?",
        #                (person_id,))
        # row = cursor.fetchone()
        # if row:
        #     return Person(row[1], row[2], row[0])
        # return None

    def update_state(self, order_id: int, state: OrderStates):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET state = %(state)s WHERE id = %(id)s",
                {"id": order_id, "state": state},
            )

    def delete(self, order_id: int):
        pass
        # cursor = self.connection.cursor()
        # cursor.execute("DELETE FROM persons WHERE id=?", (person_id,))
