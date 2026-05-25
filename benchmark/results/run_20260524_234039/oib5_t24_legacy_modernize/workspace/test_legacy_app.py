#!/usr/bin/env python3
"""Test suite for modernized inventory management system."""
import unittest
import logging
from legacy_app import InventoryItem, Inventory


class TestInventoryItem(unittest.TestCase):
    """Test InventoryItem class."""
    
    def test_init_and_repr(self):
        """Test initialization and string representation."""
        item = InventoryItem("Test Item", 10.5, 3)
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.price, 10.5)
        self.assertEqual(item.quantity, 3)
        self.assertIn("Test Item", repr(item))
        self.assertIn("10.5", repr(item))
        self.assertIn("3", repr(item))

    def test_total_value(self):
        """Test total value calculation."""
        item = InventoryItem("Test", 5.0, 4)
        self.assertEqual(item.total_value(), 20.0)
        
        # Test with decimal prices
        item = InventoryItem("Test", 2.99, 3)
        self.assertAlmostEqual(item.total_value(), 8.97, places=2)

    def test_is_low_stock(self):
        """Test low stock detection."""
        item = InventoryItem("Test", 1.0, 3)
        self.assertTrue(item.is_low_stock(5))  # 3 < 5
        self.assertFalse(item.is_low_stock(3))  # 3 not < 3
        self.assertFalse(item.is_low_stock(2))  # 3 not < 2
        
        # Test with default threshold
        item_low = InventoryItem("Low", 1.0, 4)
        item_ok = InventoryItem("Ok", 1.0, 6)
        self.assertTrue(item_low.is_low_stock())
        self.assertFalse(item_ok.is_low_stock())


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
    
    def test_add_item_existing_quantity_only(self):
        """Test adding existing item only updates quantity, not price."""
        # Add item first time
        self.inv.add_item("Widget", 9.99, 10)
        
        # Add same item again with different price (should not change price)
        self.inv.add_item("Widget", 12.99, 5)
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 15)  # 10 + 5
        self.assertEqual(item.price, 9.99)   # Original price, not 12.99
        
        # Add more with another different price
        self.inv.add_item("Widget", 7.99, 3)
        self.assertEqual(item.quantity, 18)  # 15 + 3
        self.assertEqual(item.price, 9.99)   # Still original price
    
    def test_remove_item_success(self):
        """Test successful item removal."""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.remove_item("Widget", 3)
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 7)
    
    def test_remove_item_complete(self):
        """Test removing all items removes item from inventory."""
        self.inv.add_item("Widget", 9.99, 5)
        self.inv.remove_item("Widget", 5)
        
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)  # Should be removed when quantity reaches 0
    
    def test_remove_item_not_found(self):
        """Test removing non-existent item raises exception."""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Nonexistent", 1)
        self.assertIn("not found", str(context.exception).lower())
        
        # Verify inventory remains unchanged
        self.assertEqual(len(self.inv.items), 0)
    
    def test_remove_item_insufficient_stock(self):
        """Test removing more than available raises exception."""
        self.inv.add_item("Widget", 9.99, 5)
        
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 10)
        self.assertIn("not enough", str(context.exception).lower())
        
        # Critical: Verify quantity is NOT partially modified
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)  # Should still be 5, not -5 or 0
    
    def test_get_item(self):
        """Test retrieving items."""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Gadget", 24.99, 3)
        
        widget = self.inv.get_item("Widget")
        self.assertEqual(widget.quantity, 10)
        
        gadget = self.inv.get_item("Gadget")
        self.assertEqual(gadget.quantity, 3)
        
        none_item = self.inv.get_item("Nonexistent")
        self.assertIsNone(none_item)
    
    def test_total_value(self):
        """Test total value calculation."""
        self.assertEqual(self.inv.total_value(), 0.0)  # Empty inventory
        
        self.inv.add_item("Widget", 10.0, 3)
        self.inv.add_item("Gadget", 5.0, 4)
        
        # Widget: 10 * 3 = 30, Gadget: 5 * 4 = 20, Total: 50
        self.assertEqual(self.inv.total_value(), 50.0)
        
        # Add more to existing item
        self.inv.add_item("Widget", 10.0, 2)  # Price should not change
        # Now Widget: 10 * 5 = 50, Gadget: 5 * 4 = 20, Total: 70
        self.assertEqual(self.inv.total_value(), 70.0)
    
    def test_low_stock_items(self):
        """Test low stock detection."""
        self.inv.add_item("Low1", 1.0, 2)   # Low stock
        self.inv.add_item("Low2", 2.0, 4)   # Low stock (default threshold=5)
        self.inv.add_item("Ok1", 3.0, 6)    # Not low
        self.inv.add_item("Ok2", 4.0, 10)   # Not low
        
        low_items = self.inv.low_stock_items()
        self.assertEqual(len(low_items), 2)
        names = {item.name for item in low_items}
        self.assertEqual(names, {"Low1", "Low2"})
        
        # Test with custom threshold
        low_items_threshold3 = self.inv.low_stock_items(3)
        self.assertEqual(len(low_items_threshold3), 1)
        self.assertEqual(low_items_threshold3[0].name, "Low1")
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search."""
        self.inv.add_item("Widget", 1.0, 1)
        self.inv.add_item("Gadget", 2.0, 1)
        self.inv.add_item("WIDGET_PRO", 3.0, 1)
        self.inv.add_item("Doohickey", 4.0, 1)
        
        # Search with different case variations
        results = self.inv.search("widget")
        self.assertEqual(len(results), 2)
        names = {item.name for item in results}
        self.assertEqual(names, {"Widget", "WIDGET_PRO"})
        
        # Uppercase query
        results = self.inv.search("WIDGET")
        self.assertEqual(len(results), 2)
        
        # Mixed case
        results = self.inv.search("WiDgEt")
        self.assertEqual(len(results), 2)
        
        # Partial match
        results = self.inv.search("get")
        self.assertEqual(len(results), 2)  # Widget, Gadget
        
        # No matches
        results = self.inv.search("xyz")
        self.assertEqual(len(results), 0)
    
    def test_apply_discount_success(self):
        """Test successful discount application."""
        self.inv.add_item("Widget", 100.0, 2)
        self.inv.apply_discount("Widget", 20)  # 20% discount
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 80.0)  # 100 * 0.8 = 80
        self.assertEqual(item.total_value(), 160.0)  # 80 * 2
    
    def test_apply_discount_not_found(self):
        """Test discount on non-existent item raises exception."""
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("Nonexistent", 10)
        self.assertIn("not found", str(context.exception).lower())
        
        # Verify inventory remains unchanged
        self.assertEqual(len(self.inv.items), 0)
    
    def test_apply_discount_state_preservation(self):
        """Test failed discount doesn't leave partial state."""
        # Add multiple items
        self.inv.add_item("Item1", 100.0, 2)
        self.inv.add_item("Item2", 50.0, 3)
        
        # Try to apply discount to non-existent item
        with self.assertRaises(Exception):
            self.inv.apply_discount("Item3", 10)
        
        # Verify existing items unchanged
        item1 = self.inv.get_item("Item1")
        item2 = self.inv.get_item("Item2")
        self.assertEqual(item1.price, 100.0)
        self.assertEqual(item2.price, 50.0)
        
        # Verify no partial discount was applied
        self.assertNotIn("Item3", self.inv.items)
    
    def test_apply_discount_multiple(self):
        """Test multiple discounts cumulative effect."""
        self.inv.add_item("Widget", 100.0, 1)
        
        self.inv.apply_discount("Widget", 10)  # 10% off: 100 -> 90
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 90.0)
        
        self.inv.apply_discount("Widget", 20)  # 20% off: 90 -> 72
        self.assertEqual(item.price, 72.0)
    
    def test_generate_report(self):
        """Test report generation."""
        self.inv.add_item("Banana", 0.5, 10)
        self.inv.add_item("Apple", 1.0, 5)
        
        report = self.inv.generate_report()
        
        # Check report structure
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Banana:", report)
        self.assertIn("Apple:", report)
        self.assertIn("Total:", report)
        
        # Check alphabetical order (Apple should come before Banana)
        apple_pos = report.find("Apple:")
        banana_pos = report.find("Banana:")
        self.assertLess(apple_pos, banana_pos)
        
        # Check calculations
        self.assertIn("$0.50 x 10 = $5.00", report)  # Banana
        self.assertIn("$1.00 x 5 = $5.00", report)    # Apple
        self.assertIn("Total: $10.00", report)
    
    def test_empty_inventory(self):
        """Test operations on empty inventory."""
        # Empty inventory should have zero total value
        self.assertEqual(self.inv.total_value(), 0.0)
        
        # No low stock items
        self.assertEqual(len(self.inv.low_stock_items()), 0)
        
        # Search returns empty list
        self.assertEqual(len(self.inv.search("anything")), 0)
        
        # Report should still work
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Total: $0.00", report)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Zero quantity add
        self.inv.add_item("Widget", 9.99, 0)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 0)
        
        # Zero price
        self.inv.add_item("Freebie", 0.0, 10)
        self.assertEqual(self.inv.total_value(), 0.0)
        
        # Large numbers
        self.inv.add_item("Bulk", 1.0, 1000000)
        item = self.inv.get_item("Bulk")
        self.assertEqual(item.total_value(), 1000000.0)
        
        # Decimal quantities not directly testable since API uses ints,
        # but price calculations should handle decimals
        self.inv.add_item("Decimal", 1.99, 3)
        self.assertAlmostEqual(self.inv.total_value(), 5.97, places=2)
    
    def test_discount_boundary(self):
        """Test discount boundary conditions."""
        self.inv.add_item("Widget", 100.0, 1)
        
        # 0% discount (no change)
        self.inv.apply_discount("Widget", 0)
        self.assertEqual(self.inv.get_item("Widget").price, 100.0)
        
        # 100% discount (free)
        self.inv.apply_discount("Widget", 100)
        self.assertEqual(self.inv.get_item("Widget").price, 0.0)
        
        # Reset and test 50% discount
        self.inv.add_item("Item2", 80.0, 1)
        self.inv.apply_discount("Item2", 50)
        self.assertEqual(self.inv.get_item("Item2").price, 40.0)


if __name__ == "__main__":
    # Disable logging during tests for cleaner output
    logging.disable(logging.CRITICAL)
    
    # Run tests
    unittest.main(verbosity=2)