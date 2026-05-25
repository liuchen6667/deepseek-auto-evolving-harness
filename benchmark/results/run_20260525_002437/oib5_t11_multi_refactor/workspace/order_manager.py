"""订单管理模块"""

import common

ORDER_FILE = "orders.json"


def load_orders():
    return common.load_json(ORDER_FILE)


def save_orders(orders):
    common.save_json(orders, ORDER_FILE)


def find_order(orders, order_id):
    return common.find_by_id(orders, order_id)


def validate_amount(amount):
    return isinstance(amount, (int, float)) and amount > 0