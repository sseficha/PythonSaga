import os
from contextlib import contextmanager
from typing import Optional

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from business.domains.order import Order, OrderStates
from output.base_repository import BaseRepository


class PostgresOrderRepository(BaseRepository[Order]):

    conn_str = os.environ["ORDER_DB_CONNECTION"]

    def __init__(self, conn: Connection):
        self.conn = conn

    @classmethod
    @contextmanager
    def connect(cls):
        with psycopg.connect(cls.conn_str) as conn:
            yield cls(conn)

    def add(self, order: Order) -> int:
        with self.conn.cursor() as cursor:
            order_id = cursor.execute(
                "INSERT INTO orders (user_id, state) VALUES (%(user_id)s, %(state)s) RETURNING id",
                {"user_id": order.user_id, "state": order.state},
            ).fetchone()[0]

            for item in order.items:
                cursor.execute(
                    "INSERT INTO order_items (order_id, item_id, quantity, price_per_unit) VALUES "
                    "(%(order_id)s, %(item_id)s, %(quantity)s, %(price_per_unit)s)",
                    {
                        "order_id": order_id,
                        "item_id": item.item_id,
                        "quantity": item.quantity,
                        "price_per_unit": item.price_per_unit,
                    },
                )
        return order_id

    def get_by_id(self, order_id: int) -> Optional[Order]:
        with self.conn.cursor(row_factory=dict_row) as cursor:
            res = cursor.execute(
                """SELECT * FROM orders
                    INNER JOIN order_items
                    ON orders.id = order_items.order_id
                    WHERE orders.id = %(order_id)s""",
                {"order_id": order_id},
            ).fetchall()
        if not res:
            return None
        print("*" * 100)
        print(res)
        return Order(
            id=res[0]["order_id"],
            created_at=res[0]["created_at"],
            updated_at=res[0]["updated_at"],
            state=res[0]["state"],
            user_id=res[0]["user_id"],
            items=[
                Order.OrderItem(
                    **{
                        "id": item["id"],
                        "item_id": item["item_id"],
                        "quantity": item["quantity"],
                        "price_per_unit": item["price_per_unit"],
                    }
                )
                for item in res
            ],
        )

    def update_state(self, order_id: int, state: OrderStates):
        with self.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE orders SET state = %(state)s WHERE id = %(id)s",
                {"id": order_id, "state": state},
            )
