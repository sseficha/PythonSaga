import logging
import random
import time

from .main import app


@app.task(name="check_funds")
def check_funds(order) -> dict:
    logging.info(f"Checking funds for order {order}")
    time.sleep(2)
    return {"order": order, "has_funds": random.choice([True, False])}
