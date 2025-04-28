# PythonSaga

Showcase Hexagonal Architecture and Orchestration-based Sagas.

### Running the project

Requirements: **Docker Compose**

To spin up the containers navigate to the root of the project and run:

```commandline
docker compose up
```

### Creating an order
```commandline
curl --location 'localhost/order' \
--header 'Content-Type: application/json' \
--data '{"user_id":1, "items":[{"item_id":1, "quantity":1, "price_per_unit":100}, {"item_id":2, "quantity":2, "price_per_unit":10}]}'
```
### Medium Article
[Implementing an Orchestration-Based Saga in Python](https://medium.com/@SolonSef/implementing-an-orchestration-based-saga-in-python-d0926a24b3a9)

