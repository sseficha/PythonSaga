from celery import chain, signature

from business.domains.order import Order


class CeleryAdapter:
    def __init__(
        self,
        reserve_stock: chain,
        check_funds: chain,
        no_funds_compensate: signature,
        approve_order: chain,
    ):
        self.__reserve_stock = reserve_stock
        self.__check_funds = check_funds
        self.__no_funds_compensate = no_funds_compensate
        self.__approve_order = approve_order

    def reserve_stock(self, order: Order):
        self.__reserve_stock.delay(order.id, [item.model_dump() for item in order.items])

    def check_funds(self, order: Order):
        self.__check_funds.delay(order.id, order.user_id, order.total_price)

    def no_funds_compensate(self, order: Order):
        self.__no_funds_compensate.delay(order.id, [item.model_dump() for item in order.items])

    def approve_order(self, order: Order):
        self.__approve_order.delay(order.id)
