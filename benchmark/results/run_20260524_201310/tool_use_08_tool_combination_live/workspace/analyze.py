import json
from datetime import datetime

def analyze_user_data():
    # 读取数据
    with open('sample_data.json', 'r') as f:
        data = json.load(f)
    
    users = data['users']
    
    # 统计总用户数
    total_users = len(users)
    
    # 统计 action 出现次数
    action_counts = {}
    for user in users:
        action = user['action']
        action_counts[action] = action_counts.get(action, 0) + 1
    
    # 按时间排序的用户名字
    # 先按时间戳排序
    sorted_users = sorted(users, key=lambda x: x['timestamp'])
    users_in_time_order = [user['name'] for user in sorted_users]
    
    # 创建结果字典
    result = {
        "total_users": total_users,
        "action_counts": action_counts,
        "users_in_time_order": users_in_time_order,
        "analysis_method": [
            "Combined file_read tool to read sample_data.json",
            "Used Python script to parse JSON and calculate statistics",
            "Applied sorted() function to order users by timestamp"
        ]
    }
    
    # 写入结果文件
    with open('analysis_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return result

if __name__ == "__main__":
    result = analyze_user_data()
    print("分析完成！结果已保存到 analysis_result.json")
    print(json.dumps(result, indent=2))