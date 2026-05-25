import json
import sys

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data.get('users', [])

# 统计用户数量
total_users = len(users)

# 统计action出现次数
action_counts = {
    'login': 0,
    'purchase': 0,
    'logout': 0
}

for user in users:
    action = user.get('action')
    if action in action_counts:
        action_counts[action] += 1

# 按时间排序用户名字
sorted_users = sorted(users, key=lambda x: x.get('timestamp', ''))
users_in_time_order = [user.get('name') for user in sorted_users]

# 分析方法
analysis_method = [
    "使用Python脚本读取JSON数据并解析",
    "通过遍历用户列表统计action频率",
    "使用sorted()函数按timestamp字段对用户进行排序"
]

# 构建结果
result = {
    "total_users": total_users,
    "action_counts": action_counts,
    "users_in_time_order": users_in_time_order,
    "analysis_method": analysis_method
}

# 写入结果文件
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("分析完成，结果已保存到 analysis_result.json")
print("结果:", json.dumps(result, indent=2))
