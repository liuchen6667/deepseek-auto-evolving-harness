#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Modernized inventory management system (Python 3 style)"""

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class InventoryItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return "InventoryItem({}, {}, {})".format(self.name, self.price, self.quantity)

    def __str__(self):
        return "{}: ${:.2f} x {} = ${:.2f}".format(
            self.name, self.price, self.quantity, self.total_value()
        )

    def total_value(self):
        return self.price * self.quantity

    def is_low_stock(self, threshold=5):
        return self.quantity < threshold


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, price, quantity):
        """Add item to inventory. If item already exists, only quantity is updated."""
        if name in self.items:
            # Keep original price, only update quantity
            self.items[name].quantity += quantity
            logger.info("Added %d more of %s (total: %d)", quantity, name, self.items[name].quantity)
        else:
            self.items[name] = InventoryItem(name, price, quantity)
            logger.info("Added %d of %s at $%.2f each", quantity, name, price)

    def remove_item(self, name, quantity):
        """Remove quantity of item from inventory."""
        if name not in self.items:
            raise Exception("Item not found: {}".format(name))
        
        item = self.items[name]
        if item.quantity < quantity:
            raise Exception("Not enough stock for {}".format(name))
        
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[name]
            logger.info("Removed all %d of %s", quantity, name)
        else:
            logger.info("Removed %d of %s (remaining: %d)", quantity, name, item.quantity)

    def get_item(self, name):
        """Get item by name, returns None if not found."""
        return self.items.get(name)

    def total_value(self):
        """Calculate total value of all items."""
        total = 0.0
        for item in self.items.values():
            total += item.total_value()
        return total

    def low_stock_items(self, threshold=5):
        """Get list of items with quantity below threshold."""
        return [item for item in self.items.values() if item.is_low_stock(threshold)]

    def search(self, query):
        """Search items by name (case-insensitive)."""
        query_lower = query.lower()
        return [
            item for item in self.items.values()
            if query_lower in item.name.lower()
        ]

    def apply_discount(self, name, percent):
        """Apply percentage discount to item price."""
        if name not in self.items:
            raise Exception("Item not found")
        
        item = self.items[name]
        original_price = item.price
        item.price = item.price * (100 - percent) / 100
        logger.info(
            "Applied %d%% discount to %s: $%.2f -> $%.2f",
            percent, name, original_price, item.price
        )

    def generate_report(self):
        """Generate formatted inventory report."""
        lines = []
        lines.append("=== Inventory Report ===")
        for name in sorted(self.items.keys()):
            item = self.items[name]
            lines.append(
                "{}: ${:.2f} x {} = ${:.2f}".format(
                    name, item.price, item.quantity, item.total_value()
                )
            )
        lines.append("Total: ${:.2f}".format(self.total_value()))
        return "\n".join(lines)

    def __len__(self):
        """Number of distinct items in inventory."""
        return len(self.items)


if __name__ == "__main__":
    # Example usage
    inv = Inventory()
    inv.add_item("Widget", 9.99, 100)
    inv.add_item("Gadget", 24.99, 3)
    inv.add_item("Doohickey", 4.99, 50)
    print(inv.generate_report())
    print("Low stock:", inv.low_stock_items())
