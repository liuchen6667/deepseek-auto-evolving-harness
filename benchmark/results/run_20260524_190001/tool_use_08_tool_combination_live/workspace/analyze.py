import json
import sys

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data['users']

# 1. 统计总用户数
total_users = len(users)

# 2. 统计每种 action 的出现次数
action_counts = {
    "login": 0,
    "purchase": 0,
    "logout": 0
}

for user in users:
    action = user['action']
    if action in action_counts:
        action_counts[action] += 1
    else:
        action_counts[action] = 1

# 3. 按时间排序的用户名字
sorted_users = sorted(users, key=lambda x: x['timestamp'])
users_in_time_order = [user['name'] for user in sorted_users]

# 4. 分析方法
analysis_method = [
    "使用 Python 脚本读取 JSON 文件，解析数据结构",
    "通过遍历用户列表统计 action 出现次数，按时间戳排序获取用户顺序"
]

# 创建结果
result = {
    "total_users": total_users,
    "action_counts": action_counts,
    "users_in_time_order": users_in_time_order,
    "analysis_method": analysis_method
}

# 输出结果
print(json.dumps(result, indent=2))

# 保存到文件
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\n结果已保存到 analysis_result.json")