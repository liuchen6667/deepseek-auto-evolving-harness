import json
import sys

def main():
    # 读取 JSON 文件
    with open('sample_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data.get('users', [])
    
    # 统计每种 action 的出现次数
    action_counts = {
        'login': 0,
        'purchase': 0,
        'logout': 0
    }
    
    for user in users:
        action = user.get('action')
        if action in action_counts:
            action_counts[action] += 1
    
    # 按时间戳升序排序用户
    sorted_users = sorted(users, key=lambda x: x.get('timestamp', ''))
    users_in_time_order = [user.get('name') for user in sorted_users]
    
    # 去重用户数量
    unique_users = set(users_in_time_order)
    total_users = len(unique_users)
    
    # 构建结果
    result = {
        'total_users': total_users,
        'action_counts': action_counts,
        'users_in_time_order': users_in_time_order,
        'analysis_method': [
            '使用 Python 脚本读取并解析 JSON 数据',
            '通过遍历用户列表统计 action 出现次数',
            '按 timestamp 字段对用户进行升序排序'
        ]
    }
    
    # 写入结果文件，确保中文正确编码
    with open('analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print('分析完成，结果已保存到 analysis_result.json')
    print(f'总用户数: {total_users}')
    print(f'Action 统计: {action_counts}')
    print(f'按时间排序的用户: {users_in_time_order}')

if __name__ == '__main__':
    main()