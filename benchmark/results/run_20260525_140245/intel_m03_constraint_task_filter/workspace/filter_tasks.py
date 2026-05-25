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
rejected_tasks = []

for task in tasks:
    task_id = task['id']
    reason = None
    
    # 检查规则1: 优先级不能超过max_priority
    if task['priority'] > max_priority:
        reason = f"priority {task['priority']} > max_priority {max_priority}"
    
    # 检查规则2: 类别必须在允许的类别中
    elif task['category'] not in allowed_categories:
        reason = f"category '{task['category']}' not in allowed_categories {list(allowed_categories)}"
    
    # 检查规则3: 负责人不能在黑名单中
    elif task['owner'] in blocked_owners:
        reason = f"owner '{task['owner']}' in blocked_owners {list(blocked_owners)}"
    
    if reason:
        rejected_tasks.append({
            "id": task_id,
            "reason": reason
        })
    else:
        filtered_tasks.append(task)

# 按priority升序排列过滤后的任务
filtered_tasks.sort(key=lambda x: x['priority'])

# 创建结果
result = {
    "filtered": filtered_tasks,
    "rejected": rejected_tasks,
    "summary": {
        "total": len(tasks),
        "passed": len(filtered_tasks),
        "rejected": len(rejected_tasks)
    }
}

# 写入文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Total tasks: {len(tasks)}")
print(f"Passed: {len(filtered_tasks)}")
print(f"Rejected: {len(rejected_tasks)}")