from contextlib import contextmanager

import psycopg

from business.services.order_service import OrderService
from output.postgres_order_repository import PostgresOrderRepository


@contextmanager
def order_service_postgres_context(conn_str: str):
    with psycopg.connect(conn_str) as conn:
        repository = PostgresOrderRepository(conn)
        service = OrderService(repository)
        yield service
