#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modern inventory management system (Python 3 style)"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class InventoryItem:
    """Represents an item in the inventory."""
    
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return f"InventoryItem({self.name!r}, {self.price}, {self.quantity})"

    def total_value(self):
        """Calculate total value of this item."""
        return self.price * self.quantity

    def is_low_stock(self, threshold=5):
        """Check if item quantity is below threshold."""
        return self.quantity < threshold


class Inventory:
    """Manages a collection of inventory items."""
    
    def __init__(self):
        self.items = {}

    def add_item(self, name, price, quantity):
        """Add item to inventory. If item exists, only update quantity."""
        if name in self.items:
            # Important: Only update quantity, not price
            self.items[name].quantity += quantity
        else:
            self.items[name] = InventoryItem(name, price, quantity)
        logger.info(f"Added {quantity} of {name}")

    def remove_item(self, name, quantity):
        """Remove specified quantity of item from inventory."""
        if name not in self.items:
            raise Exception(f"Item not found: {name}")
        item = self.items[name]
        if item.quantity < quantity:
            raise Exception(f"Not enough stock for {name}")
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[name]
        logger.info(f"Removed {quantity} of {name}")

    def get_item(self, name):
        """Get item by name, returns None if not found."""
        return self.items.get(name)

    def total_value(self):
        """Calculate total value of all items in inventory."""
        return sum(item.total_value() for item in self.items.values())

    def low_stock_items(self, threshold=5):
        """Get list of items with quantity below threshold."""
        return [item for item in self.items.values() if item.is_low_stock(threshold)]

    def search(self, query):
        """Search items by name (case-insensitive)."""
        query_lower = query.lower()
        return [item for item in self.items.values() if query_lower in item.name.lower()]

    def apply_discount(self, name, percent):
        """Apply percentage discount to item price."""
        if name not in self.items:
            raise Exception("Item not found")
        item = self.items[name]
        # Use float division for price calculation
        item.price = item.price * (100 - percent) / 100
        logger.info(f"Applied {percent}% discount to {name}, new price: {item.price}")

    def generate_report(self):
        """Generate inventory report as string."""
        lines = []
        lines.append("=== Inventory Report ===")
        for name in sorted(self.items.keys()):
            item = self.items[name]
            lines.append(f"{name}: ${item.price:.2f} x {item.quantity} = ${item.total_value():.2f}")
        lines.append(f"Total: ${self.total_value():.2f}")
        return "\n".join(lines)


if __name__ == "__main__":
    # Example usage
    inv = Inventory()
    inv.add_item("Widget", 9.99, 100)
    inv.add_item("Gadget", 24.99, 3)
    inv.add_item("Doohickey", 4.99, 50)
    print(inv.generate_report())
    print("Low stock:", inv.low_stock_items())