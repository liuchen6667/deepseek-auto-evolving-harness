#!/usr/bin/env python3
import json
from datetime import datetime

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data['users']

# 1. 统计总用户数
total_users = len(users)
print(f"Total users: {total_users}")

# 2. 统计 action 次数
action_counts = {"login": 0, "purchase": 0, "logout": 0}
for user in users:
    action = user['action']
    if action in action_counts:
        action_counts[action] += 1
    else:
        action_counts[action] = 1
print(f"Action counts: {action_counts}")

# 3. 按时间排序的用户名
# 将字符串时间转换为 datetime 对象以便正确排序
sorted_users = sorted(users, key=lambda x: x['timestamp'])
users_in_time_order = [user['name'] for user in sorted_users]
print(f"Users in time order: {users_in_time_order}")

# 4. 分析方法
analysis_method = [
    "使用 Python 脚本读取 JSON 数据并解析为字典对象",
    "通过遍历用户列表统计每种 action 的出现次数",
    "使用 timestamp 字段对用户列表进行升序排序，提取用户名"
]

# 创建结果字典
result = {
    "total_users": total_users,
    "action_counts": action_counts,
    "users_in_time_order": users_in_time_order,
    "analysis_method": analysis_method
}

# 写入结果文件
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("分析结果已保存到 analysis_result.json")