#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for legacy_app.py (modernized version)"""

import unittest
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入模块
from legacy_app import InventoryItem, Inventory


class TestInventoryItem(unittest.TestCase):
    """Test InventoryItem class"""
    
    def test_creation(self):
        """Test basic creation"""
        item = InventoryItem("Widget", 9.99, 10)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.quantity, 10)
    
    def test_total_value(self):
        """Test total value calculation"""
        item = InventoryItem("Gadget", 24.50, 3)
        self.assertEqual(item.total_value(), 73.50)
    
    def test_is_low_stock(self):
        """Test low stock detection"""
        item = InventoryItem("Item", 1.0, 5)
        self.assertFalse(item.is_low_stock(threshold=5))  # 正好等于阈值
        self.assertTrue(item.is_low_stock(threshold=6))   # 低于阈值
        
        item2 = InventoryItem("Item2", 1.0, 4)
        self.assertTrue(item2.is_low_stock(threshold=5))  # 低于阈值
    
    def test_repr(self):
        """Test string representation"""
        item = InventoryItem("Test", 10.5, 20)
        self.assertEqual(repr(item), "InventoryItem(Test, 10.5, 20)")


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
        inv = Inventory()
        inv.add_item("NewItem", 5.0, 10)
        item = inv.get_item("NewItem")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "NewItem")
        self.assertEqual(item.price, 5.0)
        self.assertEqual(item.quantity, 10)
    
    def test_add_item_existing_preserves_price(self):
        """Test adding existing item - price should not change, quantity should accumulate"""
        # 这是关键测试：同名商品重复时只累计数量、不悄悄改价
        inv = Inventory()
        inv.add_item("Item", 10.0, 5)
        inv.add_item("Item", 15.0, 3)  # 不同的价格，但应该忽略，保持原价
        
        item = inv.get_item("Item")
        self.assertIsNotNone(item)
        self.assertEqual(item.price, 10.0)  # 应该保持第一次的价格
        self.assertEqual(item.quantity, 8)  # 5 + 3 = 8
    
    def test_remove_item_success(self):
        """Test successful removal"""
        self.inv.remove_item("Widget", 5)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)  # 10 - 5 = 5
    
    def test_remove_item_complete(self):
        """Test removing all items removes from inventory"""
        self.inv.remove_item("Widget", 10)
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)  # 应该被删除
    
    def test_remove_item_not_found(self):
        """Test removing non-existent item raises exception"""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Nonexistent", 1)
        self.assertIn("Item not found", str(context.exception))
    
    def test_remove_item_insufficient_stock(self):
        """Test removing more than available raises exception"""
        # 失败的删除操作不能留下部分状态修改
        initial_quantity = self.inv.get_item("Widget").quantity
        
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 100)  # 尝试删除超过库存
        
        self.assertIn("Not enough stock", str(context.exception))
        
        # 验证数量没有改变（事务性）
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, initial_quantity)
    
    def test_get_item(self):
        """Test getting item"""
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        
        # 测试不存在的项目
        item = self.inv.get_item("Nonexistent")
        self.assertIsNone(item)
    
    def test_total_value(self):
        """Test total inventory value"""
        # Widget: 9.99 * 10 = 99.90
        # Gadget: 24.99 * 3 = 74.97
        # Doohickey: 4.99 * 50 = 249.50
        # Total: 99.90 + 74.97 + 249.50 = 424.37
        expected = 9.99 * 10 + 24.99 * 3 + 4.99 * 50
        self.assertAlmostEqual(self.inv.total_value(), expected, places=2)
    
    def test_low_stock_items(self):
        """Test low stock detection"""
        low_items = self.inv.low_stock_items(threshold=5)
        # Gadget 有 3 个，低于阈值 5
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0].name, "Gadget")
        
        # 测试不同的阈值
        low_items = self.inv.low_stock_items(threshold=10)
        # Widget 有 10 个，正好等于阈值，所以不算低库存
        # Gadget 有 3 个，低于阈值 10
        self.assertEqual(len(low_items), 1)
        self.assertEqual(low_items[0].name, "Gadget")
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search"""
        # 搜索仍然大小写不敏感
        results = self.inv.search("WIDGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Widget")
        
        results = self.inv.search("widget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Widget")
        
        results = self.inv.search("GET")  # 部分匹配
        self.assertEqual(len(results), 2)  # Widget 和 Gadget
        names = {item.name for item in results}
        self.assertEqual(names, {"Widget", "Gadget"})
        
        results = self.inv.search("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_apply_discount_success(self):
        """Test applying discount"""
        initial_price = self.inv.get_item("Widget").price
        self.inv.apply_discount("Widget", 10)  # 10% 折扣
        
        item = self.inv.get_item("Widget")
        expected_price = initial_price * 0.9  # 90% of original
        self.assertAlmostEqual(item.price, expected_price, places=2)
    
    def test_apply_discount_not_found(self):
        """Test applying discount to non-existent item raises exception"""
        # 失败的折扣操作不能留下部分状态修改
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("Nonexistent", 10)
        self.assertIn("Item not found", str(context.exception))
    
    def test_apply_discount_edge_cases(self):
        """Test discount edge cases"""
        # 100% 折扣
        self.inv.apply_discount("Widget", 100)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.price, 0.0)
        
        # 0% 折扣
        self.inv.add_item("TestItem", 50.0, 1)
        self.inv.apply_discount("TestItem", 0)
        item = self.inv.get_item("TestItem")
        self.assertEqual(item.price, 50.0)
    
    def test_generate_report(self):
        """Test report generation"""
        report = self.inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Widget", report)
        self.assertIn("Gadget", report)
        self.assertIn("Doohickey", report)
        self.assertIn("Total:", report)
        
        # 检查排序
        lines = report.split('\n')
        # 第一行是标题，最后一行是总计
        item_lines = [line for line in lines if ':' in line]
        item_names = [line.split(':')[0].strip() for line in item_lines]
        self.assertEqual(item_names, sorted(item_names))
    
    def test_empty_inventory(self):
        """Test empty inventory behavior"""
        inv = Inventory()
        self.assertEqual(inv.total_value(), 0)
        self.assertEqual(inv.low_stock_items(), [])
        self.assertEqual(inv.search("anything"), [])
        
        report = inv.generate_report()
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Total: $0.00", report)
        
        # 从空库存删除应该失败
        with self.assertRaises(Exception):
            inv.remove_item("Nonexistent", 1)
    
    def test_negative_quantity_handling(self):
        """Test handling of edge cases with quantities"""
        # 注意：当前实现不验证负数量，但我们可以测试边界
        inv = Inventory()
        inv.add_item("Test", 10.0, 0)  # 零数量
        item = inv.get_item("Test")
        self.assertEqual(item.quantity, 0)
        self.assertTrue(item.is_low_stock(threshold=1))
    
    def test_price_precision(self):
        """Test price precision after operations"""
        inv = Inventory()
        inv.add_item("Item", 10.0, 1)
        inv.apply_discount("Item", 33)  # 33% 折扣
        
        item = inv.get_item("Item")
        # 10.0 * (100 - 33) / 100 = 10.0 * 0.67 = 6.7
        self.assertAlmostEqual(item.price, 6.7, places=2)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)