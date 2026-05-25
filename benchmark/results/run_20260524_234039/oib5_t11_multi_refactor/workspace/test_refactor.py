#!/usr/bin/env python3
"""测试重构后的代码功能是否保持不变"""

import json
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_manager import load_users, save_users, find_user, validate_email
from order_manager import load_orders, save_orders, find_order, validate_amount


def test_user_manager():
    """测试用户管理模块"""
    print("测试用户管理模块...")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
        json.dump(test_users, f)
        temp_file = f.name
    
    try:
        # 模拟原始文件路径
        import user_manager
        user_manager.DATA_FILE = temp_file
        
        # 测试加载
        users = load_users()
        assert len(users) == 2, f"预期2个用户，实际{len(users)}个"
        assert users[0]["id"] == 1, "用户ID不匹配"
        
        # 测试查找
        user = find_user(users, 1)
        assert user["name"] == "Alice", "查找用户失败"
        
        # 测试查找不存在的用户
        user = find_user(users, 999)
        assert user is None, "查找不存在的用户应该返回None"
        
        # 测试保存
        new_user = {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        users.append(new_user)
        save_users(users)
        
        # 验证保存
        with open(temp_file) as f:
            saved_users = json.load(f)
        assert len(saved_users) == 3, "保存后应该有3个用户"
        
        # 测试验证函数
        assert validate_email("test@example.com") == True, "有效邮箱验证失败"
        assert validate_email("invalid-email") == False, "无效邮箱验证失败"
        
        print("  用户管理模块测试通过！")
        return True
    finally:
        os.unlink(temp_file)


def test_order_manager():
    """测试订单管理模块"""
    print("测试订单管理模块...")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_orders = [
            {"id": "ORD001", "amount": 100.0, "product": "Book"},
            {"id": "ORD002", "amount": 50.5, "product": "Pen"}
        ]
        json.dump(test_orders, f)
        temp_file = f.name
    
    try:
        # 模拟原始文件路径
        import order_manager
        order_manager.ORDER_FILE = temp_file
        
        # 测试加载
        orders = load_orders()
        assert len(orders) == 2, f"预期2个订单，实际{len(orders)}个"
        assert orders[0]["id"] == "ORD001", "订单ID不匹配"
        
        # 测试查找
        order = find_order(orders, "ORD001")
        assert order["amount"] == 100.0, "查找订单失败"
        
        # 测试查找不存在的订单
        order = find_order(orders, "ORD999")
        assert order is None, "查找不存在的订单应该返回None"
        
        # 测试保存
        new_order = {"id": "ORD003", "amount": 75.25, "product": "Notebook"}
        orders.append(new_order)
        save_orders(orders)
        
        # 验证保存
        with open(temp_file) as f:
            saved_orders = json.load(f)
        assert len(saved_orders) == 3, "保存后应该有3个订单"
        
        # 测试验证函数
        assert validate_amount(100) == True, "正数金额验证失败"
        assert validate_amount(50.5) == True, "正数浮点金额验证失败"
        assert validate_amount(0) == False, "零金额验证失败"
        assert validate_amount(-10) == False, "负数金额验证失败"
        assert validate_amount("100") == False, "字符串金额验证失败"
        
        print("  订单管理模块测试通过！")
        return True
    finally:
        os.unlink(temp_file)


def main():
    """主测试函数"""
    print("开始测试重构后的代码...")
    print("=" * 50)
    
    success = True
    
    try:
        success = test_user_manager() and success
    except Exception as e:
        print(f"  用户管理模块测试失败: {e}")
        success = False
    
    print()
    
    try:
        success = test_order_manager() and success
    except Exception as e:
        print(f"  订单管理模块测试失败: {e}")
        success = False
    
    print("=" * 50)
    if success:
        print("所有测试通过！重构成功。")
    else:
        print("部分测试失败。")
    
    return success


if __name__ == "__main__":
    exit(0 if main() else 1)
