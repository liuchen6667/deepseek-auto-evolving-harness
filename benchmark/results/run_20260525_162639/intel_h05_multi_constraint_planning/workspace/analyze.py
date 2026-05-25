import json

# 读取项目数据
with open('project.json') as f:
    project = json.load(f)

# 读取约束数据
with open('constraints.json') as f:
    constraints = json.load(f)

# 分析可执行任务（排除charlie）
all_tasks = project['tasks']
blocked_assignees = constraints['blocked_assignees']
budget = constraints['budget_hours']
priority_categories = constraints['priority_categories']

print("=== 任务分析 ===")
print(f"预算: {budget}小时")
print(f"被封锁人员: {blocked_assignees}")
print(f"优先级类别: {priority_categories}")

# 筛选可执行任务
executable_tasks = [t for t in all_tasks if t['assignee'] not in blocked_assignees]
print(f"\n可执行任务 ({len(executable_tasks)}个):")
for t in executable_tasks:
    print(f"  {t['id']}: {t['name']} ({t['effort_hours']}h, {t['assignee']}, 依赖: {t['depends_on']}, 类别: {t['category']})")

# 计算总effort
total_effort = sum(t['effort_hours'] for t in executable_tasks)
print(f"\n可执行任务总effort: {total_effort}小时")
print(f"是否在预算内({budget}h): {total_effort <= budget}")

# 优先级任务
priority_tasks = [t for t in executable_tasks if t['category'] in priority_categories]
print(f"\n优先级任务 ({len(priority_tasks)}个):")
for t in priority_tasks:
    print(f"  {t['id']}: {t['name']} ({t['effort_hours']}h, {t['category']})")
priority_effort = sum(t['effort_hours'] for t in priority_tasks)
print(f"优先级任务总effort: {priority_effort}小时")

# 依赖分析
def can_start(task, completed):
    return all(dep in completed for dep in task['depends_on'])

# 尝试在预算内安排任务
selected = []
remaining_budget = budget
completed_ids = []

# 按优先级排序：先选优先级类别，再考虑依赖关系
candidates = executable_tasks.copy()

while candidates and remaining_budget > 0:
    # 找出可以开始的任务（依赖已满足）
    available = [t for t in candidates if can_start(t, completed_ids)]
    
    if not available:
        break
    
    # 优先选择优先级类别的任务
    priority_available = [t for t in available if t['category'] in priority_categories]
    if priority_available:
        # 选择effort最小的优先级任务
        task = min(priority_available, key=lambda x: x['effort_hours'])
    else:
        # 选择effort最小的任务
        task = min(available, key=lambda x: x['effort_hours'])
    
    if task['effort_hours'] <= remaining_budget:
        selected.append(task)
        completed_ids.append(task['id'])
        remaining_budget -= task['effort_hours']
        candidates.remove(task)
    else:
        break

print(f"\n=== 建议执行计划 ===")
print(f"选择任务数: {len(selected)}")
selected_effort = sum(t['effort_hours'] for t in selected)
print(f"选择任务总effort: {selected_effort}小时")
print(f"剩余预算: {remaining_budget}小时")
print(f"在预算内: {selected_effort <= budget}")

print(f"\n选择的任务:")
for i, t in enumerate(selected, 1):
    print(f"  {i}. {t['id']}: {t['name']} ({t['effort_hours']}h, {t['assignee']}, 类别: {t['category']})")

# 推迟的任务
deferred = [t for t in executable_tasks if t not in selected]
print(f"\n推迟的任务 ({len(deferred)}个):")
for t in deferred:
    reason = ""
    if t['assignee'] in blocked_assignees:
        reason = "人员被封锁"
    elif t['effort_hours'] > remaining_budget:
        reason = "超出剩余预算"
    elif not can_start(t, completed_ids):
        reason = "依赖未满足"
    else:
        reason = "预算不足"
    print(f"  {t['id']}: {t['name']} ({t['effort_hours']}h) - 原因: {reason}")
