#!/usr/bin/env python3
"""测试重构后的代码"""

import user_manager
import order_manager

print("测试用户管理模块...")
users = user_manager.load_users()
print(f"加载的用户: {users}")

# 添加一个测试用户
test_user = {"id": 1, "name": "Test User", "email": "test@example.com"}
users.append(test_user)
user_manager.save_users(users)
print(f"保存的用户: {users}")

# 测试查找
found = user_manager.find_user(users, 1)
print(f"找到的用户: {found}")

# 测试验证
print(f"验证邮箱 test@example.com: {user_manager.validate_email('test@example.com')}")
print(f"验证邮箱 invalid: {user_manager.validate_email('invalid')}")

print("\n测试订单管理模块...")
orders = order_manager.load_orders()
print(f"加载的订单: {orders}")

# 添加一个测试订单
test_order = {"id": 100, "product": "Test Product", "amount": 99.99}
orders.append(test_order)
order_manager.save_orders(orders)
print(f"保存的订单: {orders}")

# 测试查找
found_order = order_manager.find_order(orders, 100)
print(f"找到的订单: {found_order}")

# 测试验证
print(f"验证金额 99.99: {order_manager.validate_amount(99.99)}")
print(f"验证金额 -10: {order_manager.validate_amount(-10)}")

print("\n测试公共模块...")
import common

# 测试公共函数
test_data = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}]
common.save_json(test_data, "test.json")
loaded = common.load_json("test.json")
print(f"保存并加载的数据: {loaded}")
found_item = common.find_by_id(loaded, 1)
print(f"找到的ID为1的项目: {found_item}")

import os
if os.path.exists("test.json"):
    os.remove("test.json")
    print("清理测试文件")