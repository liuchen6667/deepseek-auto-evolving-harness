import json

# 读取任务和规则
with open('tasks.json', 'r') as f:
    tasks_data = json.load(f)

with open('rules.json', 'r') as f:
    rules = json.load(f)

tasks = tasks_data['tasks']
max_priority = rules['max_priority']
allowed_categories = set(rules['allowed_categories'])
blocked_owners = set(rules['blocked_owners'])

filtered_tasks = []
rejected_tasks = []

for task in tasks:
    task_id = task['id']
    rejected_reasons = []
    
    # 规则1: priority ≤ max_priority
    if task['priority'] > max_priority:
        rejected_reasons.append(f"priority {task['priority']} > {max_priority}")
    
    # 规则2: category 必须在 allowed_categories 中
    if task['category'] not in allowed_categories:
        rejected_reasons.append(f"category '{task['category']}' not allowed")
    
    # 规则3: owner 不能在 blocked_owners 中
    if task['owner'] in blocked_owners:
        rejected_reasons.append(f"owner '{task['owner']}' is blocked")
    
    if rejected_reasons:
        rejected_tasks.append({
            "id": task_id,
            "reason": ", ".join(rejected_reasons)
        })
    else:
        filtered_tasks.append(task)

# 按 priority 升序排列 filtered_tasks
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

print(f"处理完成！共处理 {len(tasks)} 个任务")
print(f"通过: {len(filtered_tasks)} 个")
print(f"拒绝: {len(rejected_tasks)} 个")
print(f"结果已保存到 filtered_tasks.json")
