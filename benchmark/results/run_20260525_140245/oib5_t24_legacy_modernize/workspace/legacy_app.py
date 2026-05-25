#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modernized inventory management system (Python 3 style)"""

class InventoryItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return "InventoryItem(%s, %s, %d)" % (self.name, self.price, self.quantity)

    def total_value(self):
        return self.price * self.quantity

    def is_low_stock(self, threshold=5):
        return self.quantity < threshold


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, price, quantity):
        if name in self.items:
            self.items[name].quantity += quantity
        else:
            self.items[name] = InventoryItem(name, price, quantity)

    def remove_item(self, name, quantity):
        if name not in self.items:
            raise Exception("Item not found: %s" % name)
        item = self.items[name]
        if item.quantity < quantity:
            raise Exception("Not enough stock for %s" % name)
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[name]

    def get_item(self, name):
        return self.items.get(name)

    def total_value(self):
        total = 0
        for name, item in self.items.items():
            total += item.total_value()
        return total

    def low_stock_items(self, threshold=5):
        result = []
        for name, item in self.items.items():
            if item.is_low_stock(threshold):
                result.append(item)
        return result

    def search(self, query):
        # 保持大小写不敏感搜索
        query_lower = query.lower()
        return [item for item in self.items.values() if query_lower in item.name.lower()]

    def apply_discount(self, name, percent):
        if name not in self.items:
            raise Exception("Item not found")
        item = self.items[name]
        # 注意：Python 3 中除法默认是浮点数，这里需要浮点数结果
        item.price = item.price * (100 - percent) / 100

    def generate_report(self):
        lines = []
        lines.append("=== Inventory Report ===")
        for name in sorted(self.items.keys()):
            item = self.items[name]
            lines.append("%s: $%.2f x %d = $%.2f" % (name, item.price, item.quantity, item.total_value()))
        lines.append("Total: $%.2f" % self.total_value())
        return "\n".join(lines)


if __name__ == "__main__":
    # 示例用法（可选，不打印）
    inv = Inventory()
    inv.add_item("Widget", 9.99, 100)
    inv.add_item("Gadget", 24.99, 3)
    inv.add_item("Doohickey", 4.99, 50)
    # 不打印，只是演示功能
    report = inv.generate_report()
    low_stock = inv.low_stock_items()
    # 在实际应用中，这里可以记录日志而不是打印
    # import logging
    # logging.info(report)
    # logging.info("Low stock: %s", low_stock)