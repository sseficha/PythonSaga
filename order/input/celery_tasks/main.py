from celery import Celery

app = Celery(
    "celery_tasks",
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="redis://redis:6379/0",
    include=["input.celery_tasks.create_order_saga.tasks"],
)
