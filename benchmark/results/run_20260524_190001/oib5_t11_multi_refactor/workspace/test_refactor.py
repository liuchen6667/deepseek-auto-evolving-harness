#!/usr/bin/env python3
"""测试重构后的代码"""

import json
from pathlib import Path
import user_manager
import order_manager

# 清理测试文件
for filename in ["users.json", "orders.json"]:
    if Path(filename).exists():
        Path(filename).unlink()

print("=== 测试 user_manager ===")
# 测试加载空数据
users = user_manager.load_users()
print(f"加载用户: {users}")
assert users == []

# 测试保存和加载
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]
user_manager.save_users(users)
print(f"保存用户: {users}")

loaded_users = user_manager.load_users()
print(f"重新加载用户: {loaded_users}")
assert loaded_users == users

# 测试查找
found_user = user_manager.find_user(loaded_users, 1)
print(f"查找用户ID=1: {found_user}")
assert found_user == {"id": 1, "name": "Alice", "email": "alice@example.com"}

# 测试验证
print(f"验证邮箱 alice@example.com: {user_manager.validate_email('alice@example.com')}")
print(f"验证邮箱 invalid: {user_manager.validate_email('invalid')}")

print("\n=== 测试 order_manager ===")
# 测试加载空数据
orders = order_manager.load_orders()
print(f"加载订单: {orders}")
assert orders == []

# 测试保存和加载
orders = [
    {"id": "ORD001", "amount": 100.50, "product": "Book"},
    {"id": "ORD002", "amount": 200.00, "product": "Laptop"}
]
order_manager.save_orders(orders)
print(f"保存订单: {orders}")

loaded_orders = order_manager.load_orders()
print(f"重新加载订单: {loaded_orders}")
assert loaded_orders == orders

# 测试查找
found_order = order_manager.find_order(loaded_orders, "ORD001")
print(f"查找订单ID=ORD001: {found_order}")
assert found_order == {"id": "ORD001", "amount": 100.50, "product": "Book"}

# 测试验证
print(f"验证金额 100.50: {order_manager.validate_amount(100.50)}")
print(f"验证金额 -10: {order_manager.validate_amount(-10)}")

print("\n=== 测试公共模块 ===")
from common import load_json, save_json, find_by_id

# 测试公共函数
test_data = [{"id": 1, "name": "Test"}]
save_json(test_data, "test.json")
loaded_data = load_json("test.json")
print(f"公共函数保存/加载: {loaded_data}")
assert loaded_data == test_data

found_item = find_by_id(loaded_data, 1)
print(f"公共函数查找ID=1: {found_item}")
assert found_item == {"id": 1, "name": "Test"}

# 清理
Path("test.json").unlink()
Path("users.json").unlink()
Path("orders.json").unlink()

print("\n✅ 所有测试通过！重构成功。")
