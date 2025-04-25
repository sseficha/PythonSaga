import logging
import random
import time

from .main import app


@app.task(name="check_funds")
def check_funds(order_id, user_id, total_price) -> dict:
    logging.info(f"Checking funds for order {order_id} of user {user_id} with total price {total_price}")
    time.sleep(2)
    return {"order_id": order_id, "has_funds": random.choice([True, False])}
