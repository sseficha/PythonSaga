from celery import chain, signature

from business.domains.order import Order


class CeleryAdapter:
    def __init__(
        self,
        start_saga: signature,
        reserve_stock: chain,
        check_funds: chain,
        no_funds_compensate: signature,
        approve_order: chain,
    ):
        self.__start_saga = start_saga
        self.__reserve_stock = reserve_stock
        self.__check_funds = check_funds
        self.__no_funds_compensate = no_funds_compensate
        self.__approve_order = approve_order

    def start_saga(self, order: Order):
        self.__start_saga.delay(order.model_dump())

    def reserve_stock(self, order: Order):
        self.__reserve_stock.delay(order.model_dump())

    def check_funds(self, order: Order):
        self.__check_funds.delay(order.model_dump())

    def no_funds_compensate(self, order: Order):
        self.__no_funds_compensate.delay(order.model_dump())

    def approve_order(self, order: Order):
        self.__approve_order.delay(order.model_dump())
