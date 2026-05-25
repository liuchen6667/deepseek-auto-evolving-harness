import json

# 读取任务和规则
with open('tasks.json', 'r') as f:
    data = json.load(f)
tasks = data['tasks']

with open('rules.json', 'r') as f:
    rules = json.load(f)

max_priority = rules['max_priority']
allowed_categories = set(rules['allowed_categories'])
blocked_owners = set(rules['blocked_owners'])

filtered_tasks = []
rejected = []

for task in tasks:
    id = task['id']
    reason = None
    
    # 检查优先级
    if task['priority'] > max_priority:
        reason = f'priority > {max_priority}'
    
    # 检查分类
    elif task['category'] not in allowed_categories:
        reason = f'category not in {list(allowed_categories)}'
    
    # 检查所有者
    elif task['owner'] in blocked_owners:
        reason = f'owner in blocked list {list(blocked_owners)}'
    
    if reason:
        rejected.append({'id': id, 'reason': reason})
    else:
        filtered_tasks.append(task)

# 按 priority 升序排列
filtered_tasks.sort(key=lambda x: x['priority'])

# 构建结果
result = {
    'filtered': filtered_tasks,
    'rejected': rejected,
    'summary': {
        'total': len(tasks),
        'passed': len(filtered_tasks),
        'rejected': len(rejected)
    }
}

# 写入文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Total tasks: {len(tasks)}")
print(f"Passed: {len(filtered_tasks)}")
print(f"Rejected: {len(rejected)}")
print("Results saved to filtered_tasks.json")