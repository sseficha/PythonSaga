import logging
import random
import time

from .main import app


@app.task(name="reserve_stock")
def reserve_stock(order) -> dict:
    logging.info(f"Reserving stock for order {order}")
    time.sleep(2)
    return {"order": order, "has_stock": random.choice([True, False])}


@app.task(name="free_stock")
def free_stock(order) -> dict:
    logging.info(f"Freeing stock of order {order}")
    time.sleep(2)
    return order
