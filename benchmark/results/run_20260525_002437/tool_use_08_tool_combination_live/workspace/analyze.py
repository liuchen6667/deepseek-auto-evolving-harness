import json
import sys

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data['users']

# 1. 统计总用户数
total_users = len(users)
print(f"Total users: {total_users}")

# 2. 统计每种 action 的出现次数
action_counts = {}
for user in users:
    action = user['action']
    action_counts[action] = action_counts.get(action, 0) + 1

print(f"Action counts: {action_counts}")

# 3. 按时间排序的用户名字
sorted_users = sorted(users, key=lambda x: x['timestamp'])
users_in_time_order = [user['name'] for user in sorted_users]
print(f"Users in time order: {users_in_time_order}")

# 4. 生成结果字典
result = {
    "total_users": total_users,
    "action_counts": action_counts,
    "users_in_time_order": users_in_time_order,
    "analysis_method": ["python_script_parsing", "manual_calculation_with_bash"]
}

# 输出结果到文件
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Result saved to analysis_result.json")