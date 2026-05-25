#!/usr/bin/env python3
"""Test suite for modernized legacy_app.py"""

import unittest
import sys
import math

# 导入被测试模块
sys.path.insert(0, '.')
from legacy_app import InventoryItem, Inventory


class TestInventoryItem(unittest.TestCase):
    """测试 InventoryItem 类"""
    
    def test_initialization(self):
        """测试初始化"""
        item = InventoryItem("Widget", 9.99, 10)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.quantity, 10)
    
    def test_total_value(self):
        """测试总价值计算"""
        item = InventoryItem("Gadget", 24.99, 3)
        expected = 24.99 * 3
        self.assertAlmostEqual(item.total_value(), expected, places=2)
    
    def test_is_low_stock(self):
        """测试低库存检查"""
        item = InventoryItem("Item", 1.0, 4)
        self.assertTrue(item.is_low_stock(5))
        self.assertFalse(item.is_low_stock(3))
        
        # 测试默认阈值
        item_low = InventoryItem("Low", 1.0, 4)
        item_high = InventoryItem("High", 1.0, 6)
        self.assertTrue(item_low.is_low_stock())
        self.assertFalse(item_high.is_low_stock())
    
    def test_repr(self):
        """测试字符串表示"""
        item = InventoryItem("Test", 1.5, 10)
        repr_str = repr(item)
        self.assertIn("InventoryItem", repr_str)
        self.assertIn("Test", repr_str)
        self.assertIn("1.5", repr_str)
        self.assertIn("10", repr_str)


class TestInventory(unittest.TestCase):
    """测试 Inventory 类"""
    
    def setUp(self):
        """每个测试前的设置"""
        self.inv = Inventory()
    
    def test_add_item_new(self):
        """测试添加新商品"""
        self.inv.add_item("Widget", 9.99, 10)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        self.assertEqual(item.price, 9.99)
        self.assertEqual(item.quantity, 10)
    
    def test_add_item_existing_accumulates_quantity_only(self):
        """测试添加已存在商品：只累计数量，不修改价格"""
        # 添加初始商品
        self.inv.add_item("Widget", 9.99, 10)
        initial_item = self.inv.get_item("Widget")
        initial_price = initial_item.price
        
        # 用不同价格再次添加同名商品
        self.inv.add_item("Widget", 12.99, 5)  # 不同价格
        
        # 验证数量增加但价格保持不变
        updated_item = self.inv.get_item("Widget")
        self.assertEqual(updated_item.quantity, 15)  # 10 + 5
        self.assertEqual(updated_item.price, 9.99)   # 价格不变
        
    def test_remove_item_success(self):
        """测试成功移除商品"""
        self.inv.add_item("Widget", 9.99, 10)
        self.inv.remove_item("Widget", 3)
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 7)
    
    def test_remove_item_complete(self):
        """测试完全移除商品（数量为0时从字典删除）"""
        self.inv.add_item("Widget", 9.99, 5)
        self.inv.remove_item("Widget", 5)
        item = self.inv.get_item("Widget")
        self.assertIsNone(item)
        self.assertEqual(len(self.inv.items), 0)
    
    def test_remove_item_not_found(self):
        """测试移除不存在的商品（异常路径）"""
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Nonexistent", 1)
        self.assertIn("Item not found", str(context.exception))
        
        # 验证库存未受影响
        self.assertEqual(len(self.inv.items), 0)
    
    def test_remove_item_insufficient_stock(self):
        """测试移除数量超过库存（异常路径）"""
        self.inv.add_item("Widget", 9.99, 5)
        
        with self.assertRaises(Exception) as context:
            self.inv.remove_item("Widget", 10)
        self.assertIn("Not enough stock", str(context.exception))
        
        # 验证库存数量未受影响（原子性）
        item = self.inv.get_item("Widget")
        self.assertEqual(item.quantity, 5)
    
    def test_get_item(self):
        """测试获取商品"""
        self.inv.add_item("Widget", 9.99, 10)
        item = self.inv.get_item("Widget")
        self.assertIsNotNone(item)
        self.assertEqual(item.name, "Widget")
        
        # 测试获取不存在的商品
        nonexistent = self.inv.get_item("Nonexistent")
        self.assertIsNone(nonexistent)
    
    def test_total_value(self):
        """测试总价值计算"""
        self.inv.add_item("Widget", 10.0, 5)   # 50
        self.inv.add_item("Gadget", 20.0, 3)   # 60
        self.inv.add_item("Thingy", 5.0, 10)   # 50
        
        expected = 50 + 60 + 50  # 160
        self.assertAlmostEqual(self.inv.total_value(), expected, places=2)
    
    def test_low_stock_items(self):
        """测试低库存商品列表"""
        self.inv.add_item("Low1", 1.0, 2)      # 低库存
        self.inv.add_item("Low2", 2.0, 4)      # 低库存（阈值默认5）
        self.inv.add_item("High1", 3.0, 10)    # 正常库存
        self.inv.add_item("High2", 4.0, 8)     # 正常库存
        
        low_items = self.inv.low_stock_items()
        self.assertEqual(len(low_items), 2)
        names = {item.name for item in low_items}
        self.assertEqual(names, {"Low1", "Low2"})
        
        # 测试自定义阈值
        low_items_threshold3 = self.inv.low_stock_items(threshold=3)
        self.assertEqual(len(low_items_threshold3), 1)
        self.assertEqual(low_items_threshold3[0].name, "Low1")
    
    def test_search_case_insensitive(self):
        """测试大小写不敏感的搜索"""
        self.inv.add_item("Widget", 1.0, 1)
        self.inv.add_item("GADGET", 2.0, 1)
        self.inv.add_item("Doohickey", 3.0, 1)
        
        # 小写查询
        results = self.inv.search("widget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Widget")
        
        # 大写查询
        results = self.inv.search("GADGET")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # 混合大小写查询
        results = self.inv.search("GaDgEt")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "GADGET")
        
        # 部分匹配
        results = self.inv.search("get")
        self.assertEqual(len(results), 2)  # Widget 和 GADGET
        names = {item.name for item in results}
        self.assertEqual(names, {"Widget", "GADGET"})
    
    def test_apply_discount_success(self):
        """测试成功应用折扣"""
        self.inv.add_item("Widget", 100.0, 5)
        self.inv.apply_discount("Widget", 20)  # 20% 折扣
        
        item = self.inv.get_item("Widget")
        expected_price = 100.0 * (100 - 20) / 100  # 80.0
        self.assertAlmostEqual(item.price, expected_price, places=2)
        self.assertEqual(item.quantity, 5)  # 数量不变
    
    def test_apply_discount_not_found(self):
        """测试对不存在的商品应用折扣（异常路径）"""
        with self.assertRaises(Exception) as context:
            self.inv.apply_discount("Nonexistent", 10)
        self.assertIn("Item not found", str(context.exception))
        
        # 验证库存未受影响
        self.assertEqual(len(self.inv.items), 0)
    
    def test_apply_discount_100_percent(self):
        """测试100%折扣（边界条件）"""
        self.inv.add_item("Widget", 50.0, 10)
        self.inv.apply_discount("Widget", 100)
        
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, 0.0, places=2)
    
    def test_apply_discount_zero_percent(self):
        """测试0%折扣（边界条件）"""
        self.inv.add_item("Widget", 30.0, 5)
        original_price = self.inv.get_item("Widget").price
        
        self.inv.apply_discount("Widget", 0)
        
        item = self.inv.get_item("Widget")
        self.assertAlmostEqual(item.price, original_price, places=2)
    
    def test_generate_report(self):
        """测试生成报告"""
        self.inv.add_item("Banana", 0.5, 20)
        self.inv.add_item("Apple", 1.2, 15)
        
        report = self.inv.generate_report()
        self.assertIsInstance(report, str)
        self.assertIn("=== Inventory Report ===", report)
        self.assertIn("Banana", report)
        self.assertIn("Apple", report)
        self.assertIn("Total", report)
        
        # 验证排序（按字母顺序）
        apple_index = report.find("Apple")
        banana_index = report.find("Banana")
        self.assertLess(apple_index, banana_index, "报告应按字母顺序排序")
    
    def test_report_formatting(self):
        """测试报告格式（货币格式）"""
        self.inv.add_item("Item", 9.876, 3)
        report = self.inv.generate_report()
        
        # 检查价格格式化为两位小数
        self.assertIn("$9.88", report)  # 四舍五入
        
        # 检查总价值格式
        total_value = 9.876 * 3  # 29.628
        self.assertIn("$29.63", report)  # 四舍五入
    
    def test_integration_scenario(self):
        """集成测试场景"""
        # 创建库存
        inv = Inventory()
        
        # 添加商品
        inv.add_item("Laptop", 999.99, 5)
        inv.add_item("Mouse", 29.99, 20)
        inv.add_item("Keyboard", 79.99, 8)
        
        # 验证初始状态
        self.assertEqual(len(inv.items), 3)
        self.assertAlmostEqual(inv.total_value(), 
                              (999.99*5) + (29.99*20) + (79.99*8), 
                              places=2)
        
        # 测试低库存（默认阈值5）
        low_stock = inv.low_stock_items()
        self.assertEqual(len(low_stock), 1)  # 只有 Laptop 库存5（等于阈值，不算低库存）
        
        # 应用折扣
        inv.apply_discount("Mouse", 10)  # 10% 折扣
        mouse = inv.get_item("Mouse")
        expected_mouse_price = 29.99 * 0.9
        self.assertAlmostEqual(mouse.price, expected_mouse_price, places=2)
        
        # 移除商品
        inv.remove_item("Keyboard", 3)
        keyboard = inv.get_item("Keyboard")
        self.assertEqual(keyboard.quantity, 5)
        
        # 搜索
        results = inv.search("mouse")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Mouse")
        
        # 生成报告
        report = inv.generate_report()
        self.assertIn("Keyboard", report)
        self.assertIn("Laptop", report)
        self.assertIn("Mouse", report)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)