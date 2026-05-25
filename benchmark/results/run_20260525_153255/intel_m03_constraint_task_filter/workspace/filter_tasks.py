import json

# 读取任务和规则
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
    reason = None
    
    # 规则1: 检查优先级
    if task['priority'] > max_priority:
        reason = f"priority {task['priority']} > max_priority {max_priority}"
    
    # 规则2: 检查分类
    elif task['category'] not in allowed_categories:
        reason = f"category '{task['category']}' not in allowed categories {list(allowed_categories)}"
    
    # 规则3: 检查所有者
    elif task['owner'] in blocked_owners:
        reason = f"owner '{task['owner']}' is blocked"
    
    if reason:
        rejected_tasks.append({"id": task_id, "reason": reason})
    else:
        filtered_tasks.append(task)

# 按priority升序排序filtered_tasks
filtered_tasks.sort(key=lambda x: x['priority'])

# 创建summary
summary = {
    "total": len(tasks),
    "passed": len(filtered_tasks),
    "rejected": len(rejected_tasks)
}

# 构建最终结果
result = {
    "filtered": filtered_tasks,
    "rejected": rejected_tasks,
    "summary": summary
}

# 写入文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"Summary: total={summary['total']}, passed={summary['passed']}, rejected={summary['rejected']}")
print(f"Filtered tasks: {[t['id'] for t in filtered_tasks]}")
print(f"Rejected tasks: {[r['id'] for r in rejected_tasks]}")