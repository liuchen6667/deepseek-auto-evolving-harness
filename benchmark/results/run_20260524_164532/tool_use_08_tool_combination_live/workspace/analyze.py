import json
import sys

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data['users']

# 1. 统计用户总数
total_users = len(users)

# 2. 统计每种 action 的出现次数
action_counts = {
    'login': 0,
    'purchase': 0,
    'logout': 0
}

for user in users:
    action = user['action']
    if action in action_counts:
        action_counts[action] += 1

# 3. 按时间排序的用户名字
sorted_users = sorted(users, key=lambda x: x['timestamp'])
users_in_time_order = [user['name'] for user in sorted_users]

# 4. 分析方法
analysis_method = [
    "使用 Python 脚本解析 JSON 数据并计算统计信息",
    "通过排序算法按时间戳升序排列用户数据",
    "使用字典统计不同用户行为的出现频率"
]

# 构建结果
result = {
    "total_users": total_users,
    "action_counts": action_counts,
    "users_in_time_order": users_in_time_order,
    "analysis_method": analysis_method
}

# 输出结果
with open('analysis_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("分析完成！结果已保存到 analysis_result.json")
print(f"总用户数: {total_users}")
print(f"行为统计: {action_counts}")
print(f"按时间排序的用户: {users_in_time_order}")