#!/usr/bin/env python3
import json

# 读取数据
with open('tasks.json', 'r') as f:
    tasks_data = json.load(f)
    tasks = tasks_data['tasks']

with open('rules.json', 'r') as f:
    rules = json.load(f)

max_priority = rules['max_priority']
allowed_categories = set(rules['allowed_categories'])
blocked_owners = set(rules['blocked_owners'])

filtered_tasks = []
rejected_tasks = []

for task in tasks:
    task_id = task['id']
    priority = task['priority']
    category = task['category']
    owner = task['owner']
    
    # 检查规则
    if priority > max_priority:
        rejected_tasks.append({
            'id': task_id,
            'reason': f"priority {priority} exceeds max_priority {max_priority}"
        })
        continue
    
    if category not in allowed_categories:
        rejected_tasks.append({
            'id': task_id,
            'reason': f"category '{category}' not in allowed_categories {list(allowed_categories)}"
        })
        continue
    
    if owner in blocked_owners:
        rejected_tasks.append({
            'id': task_id,
            'reason': f"owner '{owner}' is in blocked_owners {list(blocked_owners)}"
        })
        continue
    
    # 所有规则通过
    filtered_tasks.append(task)

# 按 priority 升序排列
filtered_tasks.sort(key=lambda x: x['priority'])

# 创建结果
result = {
    'filtered': filtered_tasks,
    'rejected': rejected_tasks,
    'summary': {
        'total': len(tasks),
        'passed': len(filtered_tasks),
        'rejected': len(rejected_tasks)
    }
}

# 写入文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Total tasks: {len(tasks)}")
print(f"Passed: {len(filtered_tasks)}")
print(f"Rejected: {len(rejected_tasks)}")
print(f"Result saved to filtered_tasks.json")
