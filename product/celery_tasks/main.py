from celery import Celery

app = Celery(
    "celery_tasks",
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="redis://redis:6379/0",
    include=["celery_tasks.tasks"],
)
app.conf.task_routes = {"celery_tasks.tasks.*": {"queue": "product_request_channel"}}
