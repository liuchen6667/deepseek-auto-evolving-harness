#!/usr/bin/env python3
"""Test suite for modernized legacy_app.py"""

import unittest
import sys
from legacy_app_modernized import Inventory, InventoryItem


class TestInventoryItem(unittest.TestCase):
    def test_init_and_repr(self):
        """Test InventoryItem initialization and string representation"""
        item = InventoryItem("TestItem", 10.5, 20)
        self.assertEqual(item.name, "TestItem")
        self.assertEqual(item.price, 10.5)
        self.assertEqual(item.quantity, 20)
        self.assertIn("TestItem", repr(item))
        self.assertIn("10.5", repr(item))
        self.assertIn("20", repr(item))

    def test_total_value(self):
        """Test total value calculation"""
        item = InventoryItem("Widget", 9.99, 10)
        self.assertAlmostEqual(item.total_value(), 99.9)

    def test_is_low_stock(self):
        """Test low stock detection"""
        item = InventoryItem("Item", 1.0, 5)
        self.assertFalse(item.is_low_stock(5))  # 等于阈值，不算低库存
        self.assertTrue(item.is_low_stock(6))   # 低于更高阈值
        self.assertTrue(item.is_low_stock(10))
        
        item.quantity = 4
        self.assertTrue(item.is_low_stock(5))
        self.assertFalse(item.is_low_stock(4))


class TestInventory(unittest.TestCase):
    def setUp(self):
        """Set up a fresh inventory for each test"""
        self.inv = Inventory()

    def test_add_new_item(self):
        """Test adding a new item to inventory"""
        self.inv.add_item("Widget", 9.99, 10)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.quantity, 10)

    def test_add_existing_item_quantity_only(self):
        """Test that adding existing item only increases quantity, not price"""
        # 关键测试：同名商品重复添加时只累计数量、不悄悄改价
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.add_item("Widget", 15.0, 3)  # 不同价格添加
        
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 8)  # 5 + 3
        self.assertEqual(item.price, 10.0)  # 价格应保持第一次添加时的价格

    def test_remove_item_success(self):
        """Test successful item removal"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.remove_item("Widget", 3)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 7)

    def test_remove_item_complete(self):
        """Test removing all items removes entry from inventory"""
        self.inv.add_item("Widget", 9.99, 5)
        self.inv.remove_item("Widget", 5)
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)  # 应该被完全删除

    def test_remove_item_not_found(self):
        """Test removing non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Nonexistent", 1)
        self.assertIn("Item not found", str(context.exception))

    def test_remove_item_insufficient_stock(self):
        """Test removing more than available raises exception"""
        # 关键测试：失败的删除操作不能留下部分状态修改
        self.inv.add_item("Widget", 9.99, 5)
        
        # 初始状态检查
        initial_item = self.inv.get_item("Widget")
        initial_quantity = initial_item.quantity
        
        try:
            self.inv.remove_item("Widget", 10)  # 尝试移除超过库存的数量
        except Exception:
            pass
        
        # 验证状态未改变
        item_after_failed_removal = self.inv.get_item("Widget")
        self.assertIsNotNone(item_after_failed_removal)
        self.assertEqual(item_after_failed_removal.quantity, initial_quantity)

    def test_get_item(self):
        """Test retrieving items"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.add_item("Gadget", 24.99, 3)
        
        widget = self.inv.get_item("Widget")
        self.assertEqual(widget.name, "Widget")
        
        nonexistent = self.inv.get_item("Nonexistent")
        self.assertIsNone(nonexistent)

    def test_total_value(self):
        """Test inventory total value calculation"""
        self.inv.add_item("Widget", 10.0, 5)    # 50
        self.inv.add_item("Gadget", 20.0, 3)    # 60
        self.inv.add_item("Widget", 10.0, 2)    # 额外20，总计70
        
        total = self.inv.total_value()
        self.assertAlmostEqual(total, 50 + 60 + 20)  # 70 + 60 = 130

    def test_low_stock_items(self):
        """Test low stock detection across inventory"""
        self.inv.add_item("Widget", 10.0, 10)    # 不低
        self.inv.add_item("Gadget", 20.0, 3)     # 低（默认阈值5）
        self.inv.add_item("Doohickey", 5.0, 5)   # 不低（等于阈值）
        
        low_items = self.inv.low_stock_items()
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0].name, "Gadget")
        
        # 测试自定义阈值
        low_items_custom = self.inv.low_stock_items(threshold=7)
        self.assertEqual(len(low_items_custom), 2)  # Gadget和Widget都低

    def test_search_case_insensitive(self):
        """Test case-insensitive search functionality"""
        # 关键测试：搜索仍然大小写不敏感
        self.inv.add_item("Widget", 10.0, 5)
        self.inv.add_item("GADGET", 20.0, 3)
        self.inv.add_item("doohickey", 5.0, 10)
        self.inv.add_item("WIDGET-XL", 15.0, 2)
        
        # 搜索小写
        results = self.inv.search("widget")
        self.assertEqual(len(results), 2)  # Widget 和 WIDGET-XL
        names = {item.name for item in results}
        self.assertIn("Widget", names)
        self.assertIn("WIDGET-XL", names)
        
        # 搜索大写
        results = self.inv.search("GADGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # 搜索混合大小写
        results = self.inv.search("DoOhIcKeY")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "doohickey")
        
        # 搜索不存在的
        results = self.inv.search("nonexistent")
        self.assertEqual(len(results), 0)

    def test_apply_discount_success(self):
        """Test successful discount application"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 20)  # 20%折扣
        
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 80.0)  # 100 * 0.8 = 80
        self.assertEqual(item.quantity, 5)  # 数量不变

    def test_apply_discount_not_found(self):
        """Test discount on non-existent item raises exception"""
        # 关键测试：失败的折扣操作不能留下部分状态修改
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.add_item("Gadget", 50.0, 3)
        
        # 记录初始状态
        initial_widget_price = self.inv.get_item("Widget").price
        initial_gadget_price = self.inv.get_item("Gadget").price
        
        try:
            self.inv.apply_discount("Nonexistent", 20)
        except Exception:
            pass
        
        # 验证其他商品价格未受影响
        widget_after = self.inv.get_item("Widget")
        gadget_after = self.inv.get_item("Gadget")
        
        self.assertAlmostEqual(widget_after.price, initial_widget_price)
        self.assertAlmostEqual(gadget_after.price, initial_gadget_price)

    def test_apply_discount_zero_percent(self):
        """Test 0% discount does nothing"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 0)
        
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 100.0)

    def test_apply_discount_100_percent(self):
        """Test 100% discount makes price zero"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 100)
        
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 0.0)

    def test_generate_report(self):
        """Test report generation"""
        self.inv.add_item("Banana", 1.5, 10)
        self.inv.add_item("Apple", 2.0, 5)
        
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Apple", report)
        self.assertIn("Banana", report)
        self.assertIn("Total:", report)
        
        # 检查排序（按字母顺序）
        apple_pos = report.find("Apple")
        banana_pos = report.find("Banana")
        self.assertLess(apple_pos, banana_pos)  # Apple 应该在 Banana 前面

    def test_edge_case_empty_inventory(self):
        """Test operations on empty inventory"""
        self.assertEqual(self.inv.total_value(), 0)
        self.assertEqual(self.inv.low_stock_items(), [])
        self.assertEqual(self.inv.search("anything"), [])
        report = self.inv.generate_report()
        self.assertIn("Total: $0.00", report)

    def test_edge_case_negative_discount(self):
        """Test negative discount (price increase)"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", -10)  # -10% 折扣 = 110% 价格
        
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 110.0)  # 100 * 1.1 = 110


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)