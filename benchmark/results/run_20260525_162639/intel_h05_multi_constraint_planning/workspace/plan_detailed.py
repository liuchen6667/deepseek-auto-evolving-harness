import json

# 读取项目数据
with open('project.json') as f:
    project = json.load(f)

# 读取约束数据
with open('constraints.json') as f:
    constraints = json.load(f)

# 筛选可执行任务（排除charlie）
all_tasks = project['tasks']
blocked_assignees = constraints['blocked_assignees']
budget = constraints['budget_hours']
max_parallel = constraints['max_parallel']

executable_tasks = [t for t in all_tasks if t['assignee'] not in blocked_assignees]
priority_categories = constraints['priority_categories']

# 在预算内选择任务（基于之前的分析）
# 优先级任务：p01, p02, p04, p06, p10 (总共36小时)
selected_ids = ['p01', 'p04', 'p02', 'p10', 'p06']
selected_tasks = [t for t in executable_tasks if t['id'] in selected_ids]

# 安排执行计划（考虑依赖关系和并行限制）
def schedule_tasks(tasks, max_parallel):
    """安排任务开始日期，考虑依赖关系和并行限制"""
    # 按依赖关系排序
    task_dict = {t['id']: t for t in tasks}
    
    # 找到所有任务的依赖关系
    completed = []
    day = 1
    schedule = []
    
    # 创建一个任务完成时间的映射
    finish_times = {}
    
    # 持续安排直到所有任务完成
    while len(schedule) < len(tasks):
        # 找出当前可以开始的任务（依赖已满足且未安排）
        available = []
        for task in tasks:
            if task['id'] in [s['id'] for s in schedule]:
                continue  # 已安排
            
            # 检查依赖是否满足
            deps_satisfied = True
            for dep in task['depends_on']:
                if dep not in finish_times:
                    deps_satisfied = False
                    break
            
            if deps_satisfied:
                available.append(task)
        
        if not available:
            # 如果没有可用任务，前进到下一个时间点
            if finish_times:
                day = min(finish_times.values()) + 1
            continue
        
        # 当前正在执行的任务数
        current_running = sum(1 for ft in finish_times.values() if ft >= day)
        
        # 可以开始的新任务数
        can_start = max(0, max_parallel - current_running)
        
        if can_start == 0:
            # 没有空闲位置，前进到下一个完成时间
            day = min(ft for ft in finish_times.values() if ft >= day)
            continue
        
        # 选择任务开始（优先选择优先级任务）
        priority_available = [t for t in available if t['category'] in priority_categories]
        if priority_available:
            to_start = priority_available[:can_start]
        else:
            to_start = available[:can_start]
        
        for task in to_start:
            schedule.append({
                'id': task['id'],
                'start_day': day,
                'finish_day': day + task['effort_hours'] - 1  # 假设每天工作8小时
            })
            finish_times[task['id']] = day + task['effort_hours'] - 1
        
        # 如果有任务开始，检查是否需要等待它们完成
        if to_start:
            # 前进到下一个可能的时间点（最小完成时间）
            day = min(finish_times.values()) + 1
    
    return schedule

# 安排任务
schedule = schedule_tasks(selected_tasks, max_parallel)

print("=== 详细执行计划 ===")
print(f"最大并行任务数: {max_parallel}")
print(f"预算: {budget}小时")
print(f"选择任务数: {len(selected_tasks)}")

# 计算总effort
total_effort = sum(t['effort_hours'] for t in selected_tasks)
print(f"总effort: {total_effort}小时")
print(f"在预算内: {total_effort <= budget}")

print(f"\n安排的任务:")
for item in schedule:
    task = next(t for t in selected_tasks if t['id'] == item['id'])
    print(f"  {item['id']}: {task['name']} - 开始第{item['start_day']}天, 结束第{item['finish_day']}天 ({task['effort_hours']}h, {task['assignee']}, 类别: {task['category']})")

# 推迟的任务
deferred_tasks = [t for t in executable_tasks if t['id'] not in selected_ids]
print(f"\n推迟的任务 ({len(deferred_tasks)}个):")
for task in deferred_tasks:
    reason = ""
    if task['id'] == 'p05':
        reason = "依赖p03未完成(p03分配给被封锁人员charlie)"
    elif task['id'] == 'p07':
        reason = "预算不足(需要15小时，剩余4小时)"
    elif task['id'] == 'p09':
        reason = "预算不足(需要6小时，剩余4小时)"
    elif task['id'] == 'p11':
        reason = "依赖p07未完成"
    print(f"  {task['id']}: {task['name']} - 原因: {reason}")

# 优先级任务统计
priority_scheduled = sum(1 for t in selected_tasks if t['category'] in priority_categories)
print(f"\n已安排的优先级任务数: {priority_scheduled}")
