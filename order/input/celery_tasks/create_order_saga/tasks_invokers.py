from business.domains.order import Order
from input.celery_tasks.main import app


def invoke_reserve_stock(order: Order):
    res = app.send_task(
        "reserve_stock",
        args=(order.model_dump(),),
        queue="product_request_channel",
    )
    print("Reserve stock results!!!")
    print(res.task_id)
    print(res.get(timeout=10))
