import logging
import random

from .main import app


@app.task(name="reserve_stock", bind=True)
def reserve_stock(self, order_id) -> bool:
    logging.info(self)
    logging.info(self.request)
    logging.info(f"Reserving stock for order id {order_id}")
    # Simulate stock reservation result
    return {"order_id": order_id, "has_stock": random.choice([True, False])}
