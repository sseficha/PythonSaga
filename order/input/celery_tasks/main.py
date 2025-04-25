import os

from celery import Celery

app = Celery(
    "celery_tasks",
    broker=os.environ["RABBITMQ_CONNECTION"],
    backend=os.environ["REDIS_CONNECTION"],
    include=["input.celery_tasks.create_order_saga.tasks"],
)
