#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modernized inventory management system (Python 3 style)"""

import logging


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
        logging.info("Added %d of %s", quantity, name)

    def remove_item(self, name, quantity):
        if name not in self.items:
            raise Exception("Item not found: %s" % name)
        item = self.items[name]
        if item.quantity < quantity:
            raise Exception("Not enough stock for %s" % name)
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[name]
        logging.info("Removed %d of %s", quantity, name)

    def get_item(self, name):
        if name in self.items:
            return self.items[name]
        return None

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
        results = [item for item in self.items.values() if query.lower() in item.name.lower()]
        return results

    def apply_discount(self, name, percent):
        if name not in self.items:
            raise Exception("Item not found")
        item = self.items[name]
        item.price = item.price * (100 - percent) / 100
        logging.info("Applied %d%% discount to %s, new price: %s", percent, name, item.price)

    def generate_report(self):
        lines = []
        lines.append("=== Inventory Report ===")
        for name in sorted(self.items.keys()):
            item = self.items[name]
            lines.append("%s: $%.2f x %d = $%.2f" % (name, item.price, item.quantity, item.total_value()))
        lines.append("Total: $%.2f" % self.total_value())
        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    inv = Inventory()
    inv.add_item("Widget", 9.99, 100)
    inv.add_item("Gadget", 24.99, 3)
    inv.add_item("Doohickey", 4.99, 50)
    print(inv.generate_report())
    print("Low stock:", inv.low_stock_items())