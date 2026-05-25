import json

# 读取数据
with open('tasks.json', 'r') as f:
    tasks_data = json.load(f)
    all_tasks = tasks_data['tasks']

with open('rules.json', 'r') as f:
    rules = json.load(f)

max_priority = rules['max_priority']
allowed_categories = set(rules['allowed_categories'])
blocked_owners = set(rules['blocked_owners'])

filtered_tasks = []
rejected_tasks = []

for task in all_tasks:
    task_id = task['id']
    rejected = False
    reason = None
    
    # 规则1: 检查优先级
    if task['priority'] > max_priority:
        rejected = True
        reason = f"priority > {max_priority}"
    
    # 规则2: 检查类别
    if not rejected and task['category'] not in allowed_categories:
        rejected = True
        reason = f"category '{task['category']}' not allowed"
    
    # 规则3: 检查owner
    if not rejected and task['owner'] in blocked_owners:
        rejected = True
        reason = f"owner '{task['owner']}' is blocked"
    
    if rejected:
        rejected_tasks.append({"id": task_id, "reason": reason})
    else:
        filtered_tasks.append(task)

# 按priority升序排序
filtered_tasks.sort(key=lambda x: x['priority'])

# 创建结果
result = {
    "filtered": filtered_tasks,
    "rejected": rejected_tasks,
    "summary": {
        "total": len(all_tasks),
        "passed": len(filtered_tasks),
        "rejected": len(rejected_tasks)
    }
}

# 写入文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"处理完成: 总共{len(all_tasks)}个任务, 通过{len(filtered_tasks)}个, 拒绝{len(rejected_tasks)}个")
print(f"结果已保存到 filtered_tasks.json")
