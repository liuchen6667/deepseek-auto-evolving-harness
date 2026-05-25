#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Comprehensive tests for modernized inventory management system."""

import unittest
import logging
from legacy_app import Inventory, InventoryItem

# Suppress logging during tests
logging.getLogger().setLevel(logging.CRITICAL)


class TestInventoryItem(unittest.TestCase):
    """Test InventoryItem class."""
    
    def test_item_creation(self):
        """Test basic item creation and attributes."""
        item = InventoryItem("Test Item", 10.0, 5)
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.price, 10.0)
        self.assertEqual(item.quantity, 5)
    
    def test_total_value(self):
        """Test total value calculation."""
        item = InventoryItem("Test Item", 10.0, 5)
        self.assertEqual(item.total_value(), 50.0)
        
        # Test with float quantity
        item = InventoryItem("Test Item", 7.5, 4)
        self.assertEqual(item.total_value(), 30.0)
    
    def test_is_low_stock(self):
        """Test low stock detection."""
        item = InventoryItem("Test Item", 10.0, 5)
        # Default threshold is 5, quantity == threshold should return False
        self.assertFalse(item.is_low_stock())
        
        item.quantity = 4
        self.assertTrue(item.is_low_stock())
        
        # Test with custom threshold
        self.assertFalse(item.is_low_stock(threshold=3))
        self.assertTrue(item.is_low_stock(threshold=5))
    
    def test_repr_and_str(self):
        """Test string representations."""
        item = InventoryItem("Test Item", 10.5, 3)
        repr_str = repr(item)
        self.assertIn("Test Item", repr_str)
        self.assertIn("10.5", repr_str)
        self.assertIn("3", repr_str)
        
        str_str = str(item)
        self.assertIn("Test Item", str_str)
        self.assertIn("10.50", str_str)  # Formatted to 2 decimal places


class TestInventory(unittest.TestCase):
    """Test Inventory class."""
    
    def setUp(self):
        """Set up fresh inventory for each test."""
        self.inv = Inventory()
    
    def test_add_item_new(self):
        """Test adding new item to inventory."""
        self.inv.add_item("Widget", 9.99, 10)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.quantity, 10)
    
    def test_add_item_duplicate_quantity_only(self):
        """Test adding duplicate item - should only update quantity, not price."""
        # CRITICAL: This test verifies that price doesn't change when adding duplicate
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Widget", 12.99, 5)  # Different price!
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 15)  # Quantity should sum
        self.assertEqual(item.price, 9.99)   # Price should remain original 9.99, NOT 12.99
    
    def test_add_item_negative_quantity(self):
        """Test adding negative quantity (edge case)."""
        # This should work, negative quantities could represent returns
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Widget", 9.99, -3)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 7)
    
    def test_remove_item_success(self):
        """Test successful removal of item."""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.remove_item("Widget", 3)
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 7)
    
    def test_remove_item_complete(self):
        """Test removing all of an item removes it from inventory."""
        self.inv.add_item("Widget", 9.99, 5)
        self.inv.remove_item("Widget", 5)
        
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)
        self.assertEqual(len(self.inv), 0)
    
    def test_remove_item_not_found(self):
        """Test removing non-existent item raises exception."""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Nonexistent", 1)
        self.assertIn("Item not found", str(context.exception))
        
        # Verify inventory is unchanged
        self.assertEqual(len(self.inv), 0)
    
    def test_remove_item_insufficient_stock(self):
        """Test removing more than available raises exception."""
        # CRITICAL: This test ensures failed operation doesn't leave partial state
        self.inv.add_item("Widget", 9.99, 5)
        
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 10)
        self.assertIn("Not enough stock", str(context.exception))
        
        # Verify quantity is unchanged after failed operation
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)
    
    def test_get_item(self):
        """Test retrieving items."""
        self.assertIsNone(self.inv.get_item("Nonexistent"))
        
        self.inv.add_item("Widget", 9.99, 10)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
    
    def test_total_value_empty(self):
        """Test total value of empty inventory."""
        self.assertEqual(self.inv.total_value(), 0.0)
    
    def test_total_value_multiple_items(self):
        """Test total value calculation with multiple items."""
        self.inv.add_item("Widget", 10.0, 5)   # 50.0
        self.inv.add_item("Gadget", 20.0, 3)   # 60.0
        self.inv.add_item("Thingy", 5.0, 10)   # 50.0
        
        expected = 50.0 + 60.0 + 50.0  # 160.0
        self.assertAlmostEqual(self.inv.total_value(), expected)
    
    def test_low_stock_items(self):
        """Test low stock detection."""
        self.inv.add_item("Widget", 10.0, 10)   # Not low
        self.inv.add_item("Gadget", 20.0, 3)    # Low (default threshold 5)
        self.inv.add_item("Thingy", 5.0, 5)     # Not low (equal to threshold)
        self.inv.add_item("Doodad", 7.0, 1)     # Low
        
        low_items = self.inv.low_stock_items()
        self.assertEqual(len(low_items), 2)
        item_names = {item.name for item in low_items}
        self.assertEqual(item_names, {"Gadget", "Doodad"})
        
        # Test with custom threshold
        low_items = self.inv.low_stock_items(threshold=4)
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0].name, "Doodad")
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search."""
        # CRITICAL: This test verifies search is still case-insensitive
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.add_item("GADGET", 20.0, 3)
        self.inv.add_item("thingamajig", 5.0, 10)
        self.inv.add_item("Big Widget", 15.0, 2)
        
        # Search should be case-insensitive
        results = self.inv.search("widget")
        self.assertEqual(len(results), 2)  # "Widget" and "Big Widget"
        result_names = {item.name for item in results}
        self.assertEqual(result_names, {"Widget", "Big Widget"})
        
        results = self.inv.search("GADGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        results = self.inv.search("gadget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        results = self.inv.search("THING")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "thingamajig")
        
        # Empty search
        results = self.inv.search("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_apply_discount_success(self):
        """Test applying discount to item."""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 20)  # 20% discount
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 80.0)  # 100 * 0.8 = 80
    
    def test_apply_discount_not_found(self):
        """Test applying discount to non-existent item."""
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("Nonexistent", 10)
        self.assertIn("Item not found", str(context.exception))
    
    def test_apply_discount_edge_cases(self):
        """Test discount edge cases."""
        self.inv.add_item("Widget", 100.0, 5)
        
        # 0% discount
        self.inv.apply_discount("Widget", 0)
        self.assertEqual(self.inv.get_item("Widget").price, 100.0)
        
        # 100% discount (free)
        self.inv.apply_discount("Widget", 100)
        self.assertEqual(self.inv.get_item("Widget").price, 0.0)
        
        # Negative discount? Should increase price
        self.inv.add_item("Gadget", 100.0, 5)
        self.inv.apply_discount("Gadget", -20)  # -20% discount = 20% increase
        self.assertEqual(self.inv.get_item("Gadget").price, 120.0)
    
    def test_generate_report(self):
        """Test report generation."""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Gadget", 24.99, 3)
        
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Widget", report)
        self.assertIn("Gadget", report)
        self.assertIn("Total:", report)
        
        # Gadget should come before Widget (alphabetical)
        gadget_pos = report.find("Gadget")
        widget_pos = report.find("Widget")
        self.assertLess(gadget_pos, widget_pos)
    
    def test_len_inventory(self):
        """Test inventory length."""
        self.assertEqual(len(self.inv), 0)
        
        self.inv.add_item("Widget", 9.99, 10)
        self.assertEqual(len(self.inv), 1)
        
        self.inv.add_item("Gadget", 24.99, 3)
        self.assertEqual(len(self.inv), 2)
        
        # Adding duplicate doesn't increase length
        self.inv.add_item("Widget", 9.99, 5)
        self.assertEqual(len(self.inv), 2)
        
        # Removing all of an item decreases length
        self.inv.remove_item("Widget", 15)
        self.assertEqual(len(self.inv), 1)
    
    def test_integration_complex_scenario(self):
        """Test complex integration scenario."""
        # Start with empty inventory
        self.assertEqual(self.inv.total_value(), 0.0)
        
        # Add items
        self.inv.add_item("Apple", 1.0, 20)
        self.inv.add_item("Banana", 0.5, 30)
        self.inv.add_item("Cherry", 2.0, 2)  # Low stock
        
        # Verify counts
        self.assertEqual(len(self.inv), 3)
        self.assertAlmostEqual(self.inv.total_value(), 1.0*20 + 0.5*30 + 2.0*2)
        
        # Add more of existing item (price should not change!)
        self.inv.add_item("Apple", 1.5, 10)  # Different price!
        apple = self.inv.get_item("Apple")
        self.assertEqual(apple.quantity, 30)  # 20 + 10
        self.assertEqual(apple.price, 1.0)    # Original price, NOT 1.5
        
        # Apply discount
        self.inv.apply_discount("Banana", 10)  # 10% discount
        banana = self.inv.get_item("Banana")
        self.assertEqual(banana.price, 0.45)  # 0.5 * 0.9
        
        # Remove items
        self.inv.remove_item("Apple", 15)
        self.assertEqual(apple.quantity, 15)
        
        # Search case-insensitively
        results = self.inv.search("an")
        self.assertEqual(len(results), 2)  # Banana and Cherry (contains 'an')
        
        # Check low stock
        low_stock = self.inv.low_stock_items(threshold=5)
        self.assertEqual(len(low_stock), 2)  # Cherry (2) and now Apple (15)? Wait, threshold is 5
        # Actually Apple has 15, Banana has 30, Cherry has 2
        # So only Cherry should be low stock with threshold 5
        self.assertEqual(len(low_stock), 1)
        self.assertEqual(low_stock[0].name, "Cherry")
        
        # Generate and verify report
        report = self.inv.generate_report()
        self.assertIn("Apple", report)
        self.assertIn("Banana", report)
        self.assertIn("Cherry", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
