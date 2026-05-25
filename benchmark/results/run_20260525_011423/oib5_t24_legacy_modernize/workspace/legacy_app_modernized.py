#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modern inventory management system (Python 3 style)"""

import logging


class InventoryItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return "InventoryItem({}, {}, {})".format(self.name, self.price, self.quantity)

    def total_value(self):
        return self.price * self.quantity

    def is_low_stock(self, threshold=5):
        return self.quantity < threshold


class Inventory:
    def __init__(self):
        self.items = {}
        self.logger = logging.getLogger(__name__)

    def add_item(self, name, price, quantity):
        if name in self.items:
            self.items[name].quantity += quantity
            self.logger.info("Added %d more of %s, total: %d", quantity, name, self.items[name].quantity)
        else:
            self.items[name] = InventoryItem(name, price, quantity)
            self.logger.info("Added %d of %s at $%.2f each", quantity, name, price)

    def remove_item(self, name, quantity):
        if name not in self.items:
            raise Exception("Item not found: {}".format(name))
        item = self.items[name]
        if item.quantity < quantity:
            raise Exception("Not enough stock for {}".format(name))
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[name]
        self.logger.info("Removed %d of %s", quantity, name)

    def get_item(self, name):
        return self.items.get(name)

    def total_value(self):
        total = 0
        for item in self.items.values():
            total += item.total_value()
        return total

    def low_stock_items(self, threshold=5):
        result = []
        for item in self.items.values():
            if item.is_low_stock(threshold):
                result.append(item)
        return result

    def search(self, query):
        query_lower = query.lower()
        return [item for item in self.items.values() 
                if query_lower in item.name.lower()]

    def apply_discount(self, name, percent):
        if name not in self.items:
            raise Exception("Item not found")
        item = self.items[name]
        # 确保使用浮点数除法
        item.price = item.price * (100 - percent) / 100.0
        self.logger.info("Applied %d%% discount to %s, new price: $%.2f", 
                        percent, name, item.price)

    def generate_report(self):
        lines = []
        lines.append("=== Inventory Report ===")
        for name in sorted(self.items.keys()):
            item = self.items[name]
            lines.append("{}: ${:.2f} x {} = ${:.2f}".format(
                name, item.price, item.quantity, item.total_value()))
        lines.append("Total: ${:.2f}".format(self.total_value()))
        return "\n".join(lines)


if __name__ == "__main__":
    # 配置基本日志
    logging.basicConfig(level=logging.INFO)
    
    inv = Inventory()
    inv.add_item("Widget", 9.99, 100)
    inv.add_item("Gadget", 24.99, 3)
    inv.add_item("Doohickey", 4.99, 50)
    print(inv.generate_report())
    print("Low stock:", inv.low_stock_items())
