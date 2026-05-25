import json

# 读取数据
with open('sample_data.json', 'r') as f:
    data = json.load(f)

users = data['users']

# 1. 总用户数
total_users = len(users)
print(f'总用户数: {total_users}')

# 2. 统计action出现次数
action_counts = {'login': 0, 'purchase': 0, 'logout': 0}
for user in users:
    action = user['action']
    if action in action_counts:
        action_counts[action] += 1
    else:
        action_counts[action] = 1

print(f'Action统计: {action_counts}')

# 3. 按时间排序的用户名
sorted_users = sorted(users, key=lambda x: x['timestamp'])
users_in_time_order = [user['name'] for user in sorted_users]
print(f'按时间排序的用户名: {users_in_time_order}')

# 4. 分析方法
analysis_method = [
    '使用file_read工具读取sample_data.json文件获取原始数据',
    '编写Python脚本进行数据解析、统计和排序操作',
    '使用json模块处理JSON格式数据，确保准确解析'
]

# 创建结果字典
result = {
    'total_users': total_users,
    'action_counts': action_counts,
    'users_in_time_order': users_in_time_order,
    'analysis_method': analysis_method
}

# 写入结果文件
with open('analysis_result.json', 'w') as f:
    json.dump(result, f, indent=2)

print('分析完成，结果已保存到 analysis_result.json')