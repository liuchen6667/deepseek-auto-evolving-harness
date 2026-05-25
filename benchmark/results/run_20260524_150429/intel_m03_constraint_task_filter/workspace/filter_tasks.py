import json

# 读取数据
with open('tasks.json', 'r') as f:
    tasks_data = json.load(f)

with open('rules.json', 'r') as f:
    rules = json.load(f)

tasks = tasks_data['tasks']
max_priority = rules['max_priority']
allowed_categories = set(rules['allowed_categories'])
blocked_owners = set(rules['blocked_owners'])

filtered = []
rejected = []

for task in tasks:
    rejected_reason = None
    
    # 检查优先级
    if task['priority'] > max_priority:
        rejected_reason = f"priority > {max_priority}"
    
    # 检查类别
    elif task['category'] not in allowed_categories:
        rejected_reason = f"category '{task['category']}' not in {list(allowed_categories)}"
    
    # 检查所有者
    elif task['owner'] in blocked_owners:
        rejected_reason = f"owner '{task['owner']}' is blocked"
    
    if rejected_reason:
        rejected.append({
            'id': task['id'],
            'reason': rejected_reason
        })
    else:
        filtered.append(task)

# 按priority升序排序
filtered.sort(key=lambda x: x['priority'])

# 创建结果
result = {
    'filtered': filtered,
    'rejected': rejected,
    'summary': {
        'total': len(tasks),
        'passed': len(filtered),
        'rejected': len(rejected)
    }
}

# 写入文件
with open('filtered_tasks.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"处理完成！总共 {len(tasks)} 个任务")
print(f"通过: {len(filtered)} 个")
print(f"拒绝: {len(rejected)} 个")
print(f"结果已保存到 filtered_tasks.json")