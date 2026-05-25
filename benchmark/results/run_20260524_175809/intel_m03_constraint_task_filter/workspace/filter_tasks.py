import json

# 读取任务数据
with open('tasks.json', 'r') as f:
    data = json.load(f)
tasks = data['tasks']

# 读取过滤规则
with open('rules.json', 'r') as f:
    rules = json.load(f)

max_priority = rules['max_priority']
allowed_categories = set(rules['allowed_categories'])
blocked_owners = set(rules['blocked_owners'])

filtered_tasks = []
rejected_tasks = []

for task in tasks:
    task_id = task['id']
    
    # 检查规则1: 优先级是否 ≤ max_priority
    if task['priority'] > max_priority:
        rejected_tasks.append({
            'id': task_id,
            'reason': f'priority {task["priority"]} > max_priority {max_priority}'
        })
        continue
    
    # 检查规则2: 类别是否在允许的类别中
    if task['category'] not in allowed_categories:
        rejected_tasks.append({
            'id': task_id,
            'reason': f'category "{task["category"]}" not in allowed_categories {list(allowed_categories)}'
        })
        continue
    
    # 检查规则3: 负责人是否在阻止的负责人中
    if task['owner'] in blocked_owners:
        rejected_tasks.append({
            'id': task_id,
            'reason': f'owner "{task["owner"]}" in blocked_owners {list(blocked_owners)}'
        })
        continue
    
    # 所有规则通过
    filtered_tasks.append(task)

# 按 priority 升序排列过滤后的任务
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

# 写入结果文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"过滤完成: 总共 {len(tasks)} 个任务")
print(f"通过: {len(filtered_tasks)} 个任务")
print(f"拒绝: {len(rejected_tasks)} 个任务")
print(f"结果已保存到 filtered_tasks.json")
