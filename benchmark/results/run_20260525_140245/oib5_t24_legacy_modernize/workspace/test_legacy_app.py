#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test suite for modernized legacy_app"""

import unittest
import sys
from legacy_app import InventoryItem, Inventory


class TestInventoryItem(unittest.TestCase):
    def test_constructor_and_repr(self):
        """Test InventoryItem creation and string representation"""
        item = InventoryItem("TestItem", 10.0, 5)
        self.assertEqual(item.name, "TestItem")
        self.assertEqual(item.price, 10.0)
        self.assertEqual(item.quantity, 5)
        self.assertIn("TestItem", repr(item))
        self.assertIn("10.0", repr(item))
        self.assertIn("5", repr(item))

    def test_total_value(self):
        """Test total value calculation"""
        item = InventoryItem("Widget", 9.99, 10)
        self.assertAlmostEqual(item.total_value(), 99.9, places=2)

    def test_is_low_stock(self):
        """Test low stock detection"""
        item = InventoryItem("Item", 1.0, 3)
        self.assertTrue(item.is_low_stock(threshold=5))
        self.assertFalse(item.is_low_stock(threshold=3))
        
        item.quantity = 5
        self.assertFalse(item.is_low_stock(threshold=5))
        self.assertTrue(item.is_low_stock(threshold=6))


class TestInventory(unittest.TestCase):
    def setUp(self):
        """Set up a fresh inventory for each test"""
        self.inv = Inventory()

    # 1. add_item tests
    def test_add_item_new(self):
        """Add a new item to inventory"""
        self.inv.add_item("Widget", 10.0, 5)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 10.0)
        self.assertEqual(item.quantity, 5)

    def test_add_item_existing_accumulates_quantity_only(self):
        """Adding existing item should accumulate quantity, NOT change price"""
        # 关键测试：同名商品重复 add_item() 时只累计数量、不悄悄改价
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.add_item("Widget", 15.0, 3)  # 不同价格！
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 8)  # 5 + 3
        self.assertEqual(item.price, 10.0)  # 价格应保持第一次的 10.0，不是 15.0

    # 2. remove_item tests
    def test_remove_item_success(self):
        """Remove item successfully"""
        self.inv.add_item("Widget", 10.0, 10)
        self.inv.remove_item("Widget", 3)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 7)

    def test_remove_item_removes_when_zero(self):
        """Item should be removed from inventory when quantity reaches zero"""
        self.inv.add_item("Widget", 10.0, 3)
        self.inv.remove_item("Widget", 3)
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)

    def test_remove_item_not_found_exception(self):
        """Remove non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("NonExistent", 1)
        self.assertIn("Item not found", str(context.exception))

    def test_remove_item_insufficient_stock_exception(self):
        """Remove more than available raises exception and leaves state unchanged"""
        # 关键测试：失败的删除操作不能留下部分状态修改
        self.inv.add_item("Widget", 10.0, 5)
        
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 10)  # 尝试移除 10，但只有 5
        
        self.assertIn("Not enough stock", str(context.exception))
        # 确认数量没有被修改
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)  # 应该还是 5，没有变成 -5

    # 3. get_item tests
    def test_get_item_exists(self):
        """Get existing item"""
        self.inv.add_item("Widget", 10.0, 5)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")

    def test_get_item_not_exists(self):
        """Get non-existent item returns None"""
        item = self.inv.get_item("NonExistent")
        self.assertIsNone(item)

    # 4. total_value tests
    def test_total_value_empty(self):
        """Total value of empty inventory is zero"""
        self.assertEqual(self.inv.total_value(), 0.0)

    def test_total_value_multiple_items(self):
        """Total value with multiple items"""
        self.inv.add_item("A", 10.0, 2)  # 20
        self.inv.add_item("B", 5.0, 4)   # 20
        self.inv.add_item("C", 2.5, 8)   # 20
        self.assertAlmostEqual(self.inv.total_value(), 60.0, places=2)

    # 5. low_stock_items tests
    def test_low_stock_items_empty(self):
        """Low stock items in empty inventory"""
        self.assertEqual(self.inv.low_stock_items(), [])

    def test_low_stock_items_with_threshold(self):
        """Low stock detection with custom threshold"""
        self.inv.add_item("Low", 10.0, 3)   # low (default threshold=5)
        self.inv.add_item("High", 10.0, 10) # not low
        self.inv.add_item("Border", 10.0, 5) # not low (threshold=5)
        
        low_items = self.inv.low_stock_items(threshold=5)
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0].name, "Low")
        
        low_items_custom = self.inv.low_stock_items(threshold=8)
        self.assertEqual(len(low_items_custom), 2)
        names = {item.name for item in low_items_custom}
        self.assertEqual(names, {"Low", "Border"})

    # 6. search tests
    def test_search_case_insensitive(self):
        """Search should be case-insensitive"""
        # 关键测试：搜索仍然大小写不敏感
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.add_item("GADGET", 20.0, 3)
        self.inv.add_item("Doohickey", 5.0, 2)
        
        # 查询小写
        results = self.inv.search("widget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Widget")
        
        # 查询大写
        results = self.inv.search("GADGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # 查询混合大小写
        results = self.inv.search("GaDgEt")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # 部分匹配
        results = self.inv.search("get")
        self.assertEqual(len(results), 2)  # Widget 和 GADGET
        names = {item.name for item in results}
        self.assertEqual(names, {"Widget", "GADGET"})

    def test_search_no_results(self):
        """Search with no matches returns empty list"""
        self.inv.add_item("Widget", 10.0, 5)
        results = self.inv.search("xyz")
        self.assertEqual(results, [])

    # 7. apply_discount tests
    def test_apply_discount_success(self):
        """Apply discount successfully"""
        self.inv.add_item("Widget", 100.0, 1)
        self.inv.apply_discount("Widget", 20)  # 20% discount
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 80.0, places=2)

    def test_apply_discount_not_found_exception(self):
        """Apply discount to non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("NonExistent", 10)
        self.assertIn("Item not found", str(context.exception))

    def test_apply_discount_preserves_quantity(self):
        """Discount should only affect price, not quantity"""
        self.inv.add_item("Widget", 100.0, 10)
        self.inv.apply_discount("Widget", 50)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 10)
        self.assertAlmostEqual(item.price, 50.0, places=2)

    def test_apply_discount_failed_operation_does_not_modify_state(self):
        """Failed discount operation should not leave partial state changes"""
        # 关键测试：失败的折扣操作不能留下部分状态修改
        self.inv.add_item("Widget", 100.0, 5)
        
        with self.assertRaises(Exception):
            self.inv.apply_discount("NonExistent", 10)
        
        # 确认现有物品没有被修改
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 100.0)  # 价格应该还是 100
        self.assertEqual(item.quantity, 5)   # 数量不变

    # 8. generate_report tests
    def test_generate_report_empty(self):
        """Generate report for empty inventory"""
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Total: $0.00", report)

    def test_generate_report_with_items(self):
        """Generate report with items"""
        self.inv.add_item("Zebra", 15.0, 2)   # $30
        self.inv.add_item("Apple", 5.0, 3)    # $15
        self.inv.add_item("Banana", 2.0, 10)  # $20
        
        report = self.inv.generate_report()
        
        # 检查排序（按字母顺序）
        apple_pos = report.find("Apple")
        banana_pos = report.find("Banana")
        zebra_pos = report.find("Zebra")
        
        self.assertTrue(apple_pos < banana_pos < zebra_pos, "Items should be alphabetically sorted")
        
        # 检查内容
        self.assertIn("Apple: $5.00 x 3 = $15.00", report)
        self.assertIn("Banana: $2.00 x 10 = $20.00", report)
        self.assertIn("Zebra: $15.00 x 2 = $30.00", report)
        self.assertIn("Total: $65.00", report)

    # 额外边界测试
    def test_add_item_zero_quantity(self):
        """Add item with zero quantity"""
        self.inv.add_item("Widget", 10.0, 0)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 0)

    def test_remove_item_zero_quantity(self):
        """Remove zero quantity (edge case)"""
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.remove_item("Widget", 0)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)  # 不变

    def test_apply_discount_zero_percent(self):
        """Apply 0% discount (no change)"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 0)
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 100.0, places=2)

    def test_apply_discount_100_percent(self):
        """Apply 100% discount (price becomes zero)"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 100)
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 0.0, places=2)


def run_tests():
    """Run all tests and return success status"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)