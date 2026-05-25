import json
import sys

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data.get('users', [])

# 1. 统计总用户数
total_users = len(users)

# 2. 统计每种action的出现次数
action_counts = {"login": 0, "purchase": 0, "logout": 0}
for user in users:
    action = user.get('action')
    if action in action_counts:
        action_counts[action] += 1

# 3. 按时间排序的用户名
sorted_users = sorted(users, key=lambda x: x.get('timestamp', ''))
users_in_time_order = [user.get('name') for user in sorted_users]

# 4. 分析方法
analysis_method = [
    "使用Python脚本读取JSON文件并进行数据分析",
    "通过排序算法按时间戳对用户记录进行升序排序"
]

# 构建结果
result = {
    "total_users": total_users,
    "action_counts": action_counts,
    "users_in_time_order": users_in_time_order,
    "analysis_method": analysis_method
}

# 输出结果到文件
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("分析完成，结果已保存到 analysis_result.json")
print(json.dumps(result, indent=2))