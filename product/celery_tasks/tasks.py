import logging
import random
import time

from .main import app


@app.task(name="reserve_stock")
def reserve_stock(order_id, items) -> dict:
    logging.info(f"Reserving stock items {items} for order {order_id}")
    time.sleep(2)
    return {"order_id": order_id, "has_stock": random.choice([True, False])}


@app.task(name="free_stock")
def free_stock(order_id, items) -> int:
    logging.info(f"Freeing stock items {items} of order {order_id}")
    time.sleep(2)
    return order_id
