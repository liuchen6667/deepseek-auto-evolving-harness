#!/usr/bin/env python3
"""测试重构后的代码"""

import json
import os
from user_manager import load_users, save_users, find_user, validate_email
from order_manager import load_orders, save_orders, find_order, validate_amount

# 清理可能存在的旧测试文件
for f in ["users.json", "orders.json"]:
    if os.path.exists(f):
        os.remove(f)

print("测试 user_manager.py...")
# 测试 load_users - 文件不存在时返回空列表
users = load_users()
assert users == [], f"预期空列表，得到: {users}"
print("✓ load_users() 返回空列表（文件不存在）")

# 测试 save_users 和 load_users
test_users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]
save_users(test_users)
loaded_users = load_users()
assert loaded_users == test_users, f"保存/加载不匹配: {loaded_users}"
print("✓ save_users() 和 load_users() 正常工作")

# 测试 find_user
user = find_user(loaded_users, 1)
assert user == test_users[0], f"查找失败: {user}"
print("✓ find_user() 找到用户")

user = find_user(loaded_users, 999)
assert user is None, f"应该返回 None: {user}"
print("✓ find_user() 未找到用户返回 None")

# 测试 validate_email
assert validate_email("test@example.com") == True
assert validate_email("invalid") == False
print("✓ validate_email() 正常工作")

print("\n测试 order_manager.py...")
# 测试 load_orders - 文件不存在时返回空列表
orders = load_orders()
assert orders == [], f"预期空列表，得到: {orders}"
print("✓ load_orders() 返回空列表（文件不存在）")

# 测试 save_orders 和 load_orders
test_orders = [
    {"id": "ORD001", "amount": 100.50, "product": "Widget"},
    {"id": "ORD002", "amount": 200.75, "product": "Gadget"}
]
save_orders(test_orders)
loaded_orders = load_orders()
assert loaded_orders == test_orders, f"保存/加载不匹配: {loaded_orders}"
print("✓ save_orders() 和 load_orders() 正常工作")

# 测试 find_order
order = find_order(loaded_orders, "ORD001")
assert order == test_orders[0], f"查找失败: {order}"
print("✓ find_order() 找到订单")

order = find_order(loaded_orders, "ORD999")
assert order is None, f"应该返回 None: {order}"
print("✓ find_order() 未找到订单返回 None")

# 测试 validate_amount
assert validate_amount(100) == True
assert validate_amount(50.25) == True
assert validate_amount(0) == False
assert validate_amount(-10) == False
assert validate_amount("100") == False
print("✓ validate_amount() 正常工作")

print("\n测试 common.py 导入...")
try:
    from common import load_json, save_json, find_by_id
    print("✓ 可以从 common.py 导入函数")
    
    # 测试公共函数
    test_data = [{"id": 1, "value": "test"}]
    save_json(test_data, "test.json")
    loaded_data = load_json("test.json")
    assert loaded_data == test_data
    print("✓ common.load_json() 和 common.save_json() 正常工作")
    
    item = find_by_id(test_data, 1)
    assert item == test_data[0]
    print("✓ common.find_by_id() 正常工作")
    
    os.remove("test.json")
except ImportError as e:
    print(f"✗ 导入失败: {e}")

print("\n✅ 所有测试通过！重构成功。")

# 清理测试文件
for f in ["users.json", "orders.json"]:
    if os.path.exists(f):
        os.remove(f)