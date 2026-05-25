import json

# 读取任务和规则
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
    reasons = []
    
    # 规则1: priority 不能超过 max_priority
    if task['priority'] > max_priority:
        reasons.append(f'priority {task["priority"]} > max_priority {max_priority}')
    
    # 规则2: category 必须在 allowed_categories 中
    if task['category'] not in allowed_categories:
        reasons.append(f'category {task["category"]} not in {list(allowed_categories)}')
    
    # 规则3: owner 不能在 blocked_owners 中
    if task['owner'] in blocked_owners:
        reasons.append(f'owner {task["owner"]} is blocked')
    
    if reasons:
        rejected_tasks.append({
            'id': task_id,
            'reason': '; '.join(reasons)
        })
    else:
        filtered_tasks.append(task)

# 按 priority 升序排列 filtered_tasks
filtered_tasks.sort(key=lambda x: x['priority'])

# 生成 summary
total = len(all_tasks)
passed = len(filtered_tasks)
rejected = len(rejected_tasks)
summary = {
    'total': total,
    'passed': passed,
    'rejected': rejected
}

# 构建输出数据结构
output = {
    'filtered': filtered_tasks,
    'rejected': rejected_tasks,
    'summary': summary
}

# 写入 filtered_tasks.json
with open('filtered_tasks.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f'过滤完成: 总共 {total} 个任务, 通过 {passed} 个, 拒绝 {rejected} 个')