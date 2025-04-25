import os

from celery import Celery


app = Celery(
    "celery_tasks",
    broker=os.environ["RABBITMQ_CONNECTION"],
    backend=os.environ["REDIS_CONNECTION"],
    include=["celery_tasks.tasks"],
)
