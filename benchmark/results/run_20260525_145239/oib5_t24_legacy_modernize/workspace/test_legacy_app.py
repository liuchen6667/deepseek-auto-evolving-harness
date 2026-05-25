#!/usr/bin/env python3
"""Test suite for legacy_app.py"""

import unittest
from legacy_app import Inventory, InventoryItem


class TestInventoryItem(unittest.TestCase):
    def test_initialization(self):
        """Test InventoryItem initialization"""
        item = InventoryItem("TestItem", 10.0, 5)
        self.assertEqual(item.name, "TestItem")
        self.assertEqual(item.price, 10.0)
        self.assertEqual(item.quantity, 5)

    def test_total_value(self):
        """Test total value calculation"""
        item = InventoryItem("TestItem", 10.5, 3)
        self.assertEqual(item.total_value(), 31.5)

    def test_is_low_stock(self):
        """Test low stock detection"""
        item = InventoryItem("TestItem", 10.0, 3)
        self.assertTrue(item.is_low_stock(5))
        self.assertFalse(item.is_low_stock(3))
        self.assertTrue(item.is_low_stock(4))
        self.assertFalse(item.is_low_stock(2))

    def test_is_low_stock_custom_threshold(self):
        """Test low stock with custom threshold"""
        item = InventoryItem("TestItem", 10.0, 10)
        self.assertFalse(item.is_low_stock(5))
        self.assertTrue(item.is_low_stock(15))


class TestInventory(unittest.TestCase):
    def setUp(self):
        """Set up fresh inventory for each test"""
        self.inv = Inventory()

    def test_add_item_new(self):
        """Test adding new item"""
        self.inv.add_item("Widget", 9.99, 10)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.quantity, 10)

    def test_add_item_existing_accumulates_quantity(self):
        """Test adding existing item accumulates quantity without changing price"""
        # Add item first time
        self.inv.add_item("Widget", 9.99, 10)
        item1 = self.inv.get_item("Widget")
        
        # Add same item again with different price (should ignore price change)
        self.inv.add_item("Widget", 12.99, 5)
        item2 = self.inv.get_item("Widget")
        
        # Quantity should accumulate
        self.assertEqual(item2.quantity, 15)
        # Price should remain the original price (first added)
        self.assertEqual(item2.price, 9.99)
        self.assertNotEqual(item2.price, 12.99)

    def test_remove_item_success(self):
        """Test successful removal"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.remove_item("Widget", 5)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)

    def test_remove_item_complete_removal(self):
        """Test removing all items deletes entry"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.remove_item("Widget", 10)
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)
        self.assertEqual(len(self.inv.items), 0)

    def test_remove_item_not_found_exception(self):
        """Test removing non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("NonExistent", 5)
        self.assertIn("Item not found", str(context.exception))
        # Ensure inventory remains unchanged
        self.assertEqual(len(self.inv.items), 0)

    def test_remove_item_insufficient_stock_exception(self):
        """Test removing more than available raises exception"""
        self.inv.add_item("Widget", 9.99, 10)
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 15)
        self.assertIn("Not enough stock", str(context.exception))
        # Verify quantity unchanged (transaction rolled back)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 10)

    def test_get_item(self):
        """Test getting item"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Gadget", 19.99, 5)
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.name, "Widget")
        
        non_existent = self.inv.get_item("NonExistent")
        self.assertIsNone(non_existent)

    def test_total_value(self):
        """Test total inventory value"""
        self.inv.add_item("Widget", 10.0, 5)   # 50
        self.inv.add_item("Gadget", 20.0, 3)   # 60
        self.inv.add_item("Thingy", 5.0, 10)   # 50
        
        self.assertEqual(self.inv.total_value(), 160.0)

    def test_low_stock_items(self):
        """Test low stock detection"""
        self.inv.add_item("Widget", 10.0, 10)   # not low
        self.inv.add_item("Gadget", 20.0, 3)    # low
        self.inv.add_item("Thingy", 5.0, 5)     # borderline (not low)
        self.inv.add_item("Doodad", 15.0, 1)    # low
        
        low_items = self.inv.low_stock_items()
        self.assertEqual(len(low_items), 2)
        names = {item.name for item in low_items}
        self.assertEqual(names, {"Gadget", "Doodad"})

    def test_low_stock_items_custom_threshold(self):
        """Test low stock with custom threshold"""
        self.inv.add_item("Widget", 10.0, 10)
        self.inv.add_item("Gadget", 20.0, 7)
        self.inv.add_item("Thingy", 5.0, 5)
        
        # With threshold=8, only Widget (10) is not low
        low_items = self.inv.low_stock_items(8)
        self.assertEqual(len(low_items), 2)
        names = {item.name for item in low_items}
        self.assertEqual(names, {"Gadget", "Thingy"})

    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.add_item("GADGET", 20.0, 3)
        self.inv.add_item("thingy", 5.0, 10)
        self.inv.add_item("WIDGET-SPECIAL", 15.0, 2)
        
        # Search for "widget" should find all variations
        results = self.inv.search("widget")
        self.assertEqual(len(results), 2)
        names = {item.name for item in results}
        self.assertEqual(names, {"Widget", "WIDGET-SPECIAL"})
        
        # Search for "GADGET" should find uppercase entry
        results = self.inv.search("GADGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # Search for "gadget" (lowercase) should also find uppercase entry
        results = self.inv.search("gadget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # Partial match
        results = self.inv.search("thin")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "thingy")

    def test_apply_discount_success(self):
        """Test successful discount application"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 20)  # 20% discount
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 80.0)  # 100 * 0.8
        self.assertEqual(item.quantity, 5)

    def test_apply_discount_not_found_exception(self):
        """Test discount on non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("NonExistent", 10)
        self.assertIn("Item not found", str(context.exception))
        # Inventory should remain unchanged
        self.assertEqual(len(self.inv.items), 0)

    def test_apply_discount_edge_cases(self):
        """Test discount edge cases"""
        self.inv.add_item("Widget", 100.0, 5)
        
        # 0% discount
        self.inv.apply_discount("Widget", 0)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 100.0)
        
        # 100% discount (free)
        self.inv.apply_discount("Widget", 100)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 0.0)

    def test_generate_report(self):
        """Test report generation"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Gadget", 24.99, 3)
        
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Gadget: $24.99 x 3 = $74.97", report)
        self.assertIn("Widget: $9.99 x 10 = $99.90", report)
        self.assertIn("Total: $174.87", report)
        
        # Check ordering (alphabetical)
        gadget_pos = report.find("Gadget")
        widget_pos = report.find("Widget")
        self.assertLess(gadget_pos, widget_pos)  # Gadget comes before Widget

    def test_generate_report_empty(self):
        """Test report on empty inventory"""
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Total: $0.00", report)

    def test_failed_operations_leave_state_unchanged(self):
        """Test that failed operations don't leave partial state changes"""
        # Add initial items
        self.inv.add_item("Widget", 10.0, 10)
        self.inv.add_item("Gadget", 20.0, 5)
        
        # Try to remove more than available (should fail)
        try:
            self.inv.remove_item("Widget", 15)
        except Exception:
            pass
        
        # Verify Widget quantity unchanged
        widget = self.inv.get_item("Widget")
        self.assertEqual(widget.quantity, 10)
        
        # Try discount on non-existent item (should fail)
        try:
            self.inv.apply_discount("NonExistent", 10)
        except Exception:
            pass
        
        # Verify inventory still has only 2 items
        self.assertEqual(len(self.inv.items), 2)
        
        # Try to remove non-existent item (should fail)
        try:
            self.inv.remove_item("Thingy", 5)
        except Exception:
            pass
        
        # Verify inventory unchanged
        self.assertEqual(self.inv.total_value(), 200.0)  # 10*10 + 20*5


if __name__ == "__main__":
    unittest.main()
