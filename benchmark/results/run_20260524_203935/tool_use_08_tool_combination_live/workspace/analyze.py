#!/usr/bin/env python3
import json
from datetime import datetime

def analyze_data():
    # 读取 sample_data.json
    with open('sample_data.json', 'r') as f:
        data = json.load(f)
    
    users = data.get('users', [])
    
    # 统计每种 action 的出现次数
    action_counts = {
        "login": 0,
        "purchase": 0,
        "logout": 0
    }
    
    # 按时间排序的用户名列表
    users_sorted_by_time = []
    
    for user in users:
        action = user.get('action', '')
        if action in action_counts:
            action_counts[action] += 1
    
    # 按时间戳排序
    sorted_users = sorted(users, key=lambda x: x.get('timestamp', ''))
    
    # 提取排序后的用户名
    users_sorted_by_time = [user.get('name', '') for user in sorted_users]
    
    # 统计唯一用户数量
    unique_users = set(user.get('name', '') for user in users)
    total_users = len(unique_users)
    
    # 分析方法描述
    analysis_method = [
        "使用Python脚本读取JSON数据并进行统计分析",
        "组合使用file_read工具了解数据结构，然后编写分析脚本"
    ]
    
    # 构建结果
    result = {
        "total_users": total_users,
        "action_counts": action_counts,
        "users_in_time_order": users_sorted_by_time,
        "analysis_method": analysis_method
    }
    
    # 写入结果文件
    with open('analysis_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("分析完成！结果已保存到 analysis_result.json")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    analyze_data()