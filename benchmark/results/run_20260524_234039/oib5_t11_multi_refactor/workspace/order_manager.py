"""订单管理模块"""

from common import load_json, save_json, find_by_id

ORDER_FILE = "orders.json"


def load_orders():
    return load_json(ORDER_FILE)


def save_orders(orders):
    save_json(orders, ORDER_FILE)


def find_order(orders, order_id):
    return find_by_id(orders, order_id)


def validate_amount(amount):
    return isinstance(amount, (int, float)) and amount > 0
