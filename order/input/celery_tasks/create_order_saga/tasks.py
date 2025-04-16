import logging

from celery import signature, chain

from business.domains.order import Order
from input.celery_tasks.create_order_saga.tasks_invokers import invoke_reserve_stock
from input.celery_tasks.main import app


@app.task(name="start_create_order_saga")
def start_create_order_saga(order: Order):
    print(order)
    logging.info("Saga started")
    return order["id"]


@app.task(name="handle_reserve_stock_reply")
def handle_reserve_stock_reply(reply):
    logging.info(f"Handle order : {reply}")


create_order_saga_chain = chain(
    start_create_order_saga.s()
    | signature("reserve_stock", queue="product_request_channel")
    | handle_reserve_stock_reply.s()
)

# create order (business) with state "CREATED"


# @app.task(name="create_order_saga", pydantic=True)
# def create_order_saga(order: Order):
#     logging.info("saga started")
#     logging.info(order)
#
#     # TODO start creating chain
#
#     invoke_reserve_stock(order)
# update order (business) with state stock_reservation_pending

# call reserve_stock and get reply

# if reply is not ok
#     update order state (business) with state stock_reservation_failed
# else
#     update order state (business) with state fund_check_pending

# call account_check and get reply

# if reply is not ok
#   update order state (business) with state fund_check_failed
#   rollback stock reservation
# else
#   update order state (business) with state approved

# res = app.send_task(
#     "celery_tasks.tasks.check_stock",
#     args=({"a": "a"},),
#     queue="product_request_channel",
# )
# logging.info(res.get(timeout=10))
