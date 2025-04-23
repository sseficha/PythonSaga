from celery import Celery

from config import RABBITMQ_CONNECTION, REDIS_CONNECTION

app = Celery(
    "celery_tasks",
    broker=RABBITMQ_CONNECTION,
    backend=REDIS_CONNECTION,
    include=["input.celery_tasks.create_order_saga.tasks"],
)
