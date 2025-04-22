from contextlib import contextmanager

import psycopg

from business.services.order_service import OrderService
from output.order_repository import OrderRepository


@contextmanager
def postgres_adapter_order_service(conn_str: str):
    with psycopg.connect(conn_str) as conn:
        repository = OrderRepository(conn)
        service = OrderService(repository)
        yield service
