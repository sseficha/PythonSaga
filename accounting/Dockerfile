FROM python:3.12

RUN pip install poetry==2.*

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock

RUN poetry config virtualenvs.create false
RUN poetry install

COPY celery_tasks /code/celery_tasks

CMD ["watchmedo", "auto-restart", "--patterns=*.py", "--directory=./celery_tasks", "--recursive", "--", "celery", "-A", "celery_tasks.main:app", "worker", "-Q", "accounting_request_channel", "-l", "INFO"]