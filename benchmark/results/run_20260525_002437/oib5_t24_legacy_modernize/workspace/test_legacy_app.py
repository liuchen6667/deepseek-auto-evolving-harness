#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test suite for legacy_app.py"""

import unittest
from legacy_app import Inventory, InventoryItem


class TestInventoryItem(unittest.TestCase):
    """Test InventoryItem class"""
    
    def test_initialization(self):
        """Test basic initialization"""
        item = InventoryItem("Test", 10.0, 5)
        self.assertEqual(item.name, "Test")
        self.assertEqual(item.price, 10.0)
        self.assertEqual(item.quantity, 5)
    
    def test_total_value(self):
        """Test total value calculation"""
        item = InventoryItem("Test", 10.0, 5)
        self.assertEqual(item.total_value(), 50.0)
        
        item = InventoryItem("Test", 7.5, 3)
        self.assertEqual(item.total_value(), 22.5)
    
    def test_is_low_stock(self):
        """Test low stock detection"""
        item = InventoryItem("Test", 10.0, 5)
        self.assertFalse(item.is_low_stock())  # default threshold=5
        self.assertTrue(item.is_low_stock(6))  # threshold=6
        
        item = InventoryItem("Test", 10.0, 4)
        self.assertTrue(item.is_low_stock())
        self.assertFalse(item.is_low_stock(3))


class TestInventory(unittest.TestCase):
    """Test Inventory class"""
    
    def setUp(self):
        """Set up test inventory"""
        self.inv = Inventory()
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Gadget", 24.99, 3)
        self.inv.add_item("Doohickey", 4.99, 50)
    
    def test_add_item_new(self):
        """Test adding new item"""
        self.inv.add_item("NewItem", 15.0, 20)
        item = self.inv.get_item("NewItem")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "NewItem")
        self.assertEqual(item.price, 15.0)
        self.assertEqual(item.quantity, 20)
    
    def test_add_item_duplicate_accumulate_quantity(self):
        """Test adding duplicate item accumulates quantity but doesn't change price"""
        # Add same item again
        self.inv.add_item("Widget", 999.99, 5)  # Different price, should be ignored
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 15)  # 10 + 5 = 15
        self.assertEqual(item.price, 9.99)   # Price should remain unchanged
    
    def test_remove_item_success(self):
        """Test successful removal"""
        self.inv.remove_item("Widget", 5)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)  # 10 - 5 = 5
    
    def test_remove_item_complete(self):
        """Test removal that empties stock removes item"""
        self.inv.remove_item("Widget", 10)
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)
    
    def test_remove_item_not_found(self):
        """Test removal of non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Nonexistent", 1)
        self.assertIn("Item not found", str(context.exception))
        
        # Verify inventory state unchanged
        self.assertIsNotNone(self.inv.get_item("Widget"))
        self.assertIsNotNone(self.inv.get_item("Gadget"))
        self.assertIsNotNone(self.inv.get_item("Doohickey"))
    
    def test_remove_item_insufficient_stock(self):
        """Test removal with insufficient stock raises exception and leaves state unchanged"""
        initial_quantity = self.inv.get_item("Widget").quantity
        
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 100)
        self.assertIn("Not enough stock", str(context.exception))
        
        # Verify quantity unchanged
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, initial_quantity)
    
    def test_get_item(self):
        """Test getting item"""
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        
        item = self.inv.get_item("Nonexistent")
        self.assertIsNone(item)
    
    def test_total_value(self):
        """Test total inventory value"""
        # Widget: 9.99 * 10 = 99.9
        # Gadget: 24.99 * 3 = 74.97
        # Doohickey: 4.99 * 50 = 249.5
        # Total: 99.9 + 74.97 + 249.5 = 424.37
        expected = 9.99 * 10 + 24.99 * 3 + 4.99 * 50
        self.assertAlmostEqual(self.inv.total_value(), expected, places=2)
    
    def test_low_stock_items(self):
        """Test low stock detection"""
        low_items = self.inv.low_stock_items()
        self.assertEqual(len(low_items), 1)  # Only Gadget has quantity 3 < 5
        self.assertEqual(low_items[0].name, "Gadget")
        
        # Test with custom threshold
        low_items = self.inv.low_stock_items(threshold=10)
        self.assertEqual(len(low_items), 1)  # Only Gadget (3) < 10, Widget (10) not < 10, Doohickey (50) not < 10
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search"""
        results = self.inv.search("WIDGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Widget")
        
        results = self.inv.search("widget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Widget")
        
        results = self.inv.search("get")
        self.assertEqual(len(results), 2)  # Widget and Gadget
        
        results = self.inv.search("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_apply_discount_success(self):
        """Test successful discount application"""
        self.inv.apply_discount("Widget", 10)  # 10% discount
        item = self.inv.get_item("Widget")
        expected_price = 9.99 * 0.9  # 10% discount
        self.assertAlmostEqual(item.price, expected_price, places=2)
    
    def test_apply_discount_not_found(self):
        """Test discount on non-existent item raises exception"""
        initial_prices = {
            "Widget": self.inv.get_item("Widget").price,
            "Gadget": self.inv.get_item("Gadget").price,
            "Doohickey": self.inv.get_item("Doohickey").price
        }
        
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("Nonexistent", 10)
        self.assertIn("Item not found", str(context.exception))
        
        # Verify no prices were changed
        for name, expected_price in initial_prices.items():
            self.assertEqual(self.inv.get_item(name).price, expected_price)
    
    def test_apply_discount_edge_cases(self):
        """Test discount edge cases"""
        # 0% discount
        self.inv.apply_discount("Widget", 0)
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 9.99, places=2)
        
        # 100% discount
        self.inv.apply_discount("Gadget", 100)
        item = self.inv.get_item("Gadget")
        self.assertAlmostEqual(item.price, 0.0, places=2)
    
    def test_generate_report(self):
        """Test report generation"""
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Widget", report)
        self.assertIn("Gadget", report)
        self.assertIn("Doohickey", report)
        self.assertIn("Total:", report)
        
        # Check ordering (should be alphabetical)
        widget_pos = report.find("Widget")
        gadget_pos = report.find("Gadget")
        doohickey_pos = report.find("Doohickey")
        
        # Doohickey should come before Gadget which should come before Widget
        # (alphabetical: Doohickey, Gadget, Widget)
        self.assertTrue(doohickey_pos < gadget_pos < widget_pos)
    
    def test_empty_inventory(self):
        """Test operations on empty inventory"""
        empty_inv = Inventory()
        
        self.assertEqual(empty_inv.total_value(), 0)
        self.assertEqual(empty_inv.low_stock_items(), [])
        self.assertEqual(empty_inv.search("anything"), [])
        
        report = empty_inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Total: $0.00", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)