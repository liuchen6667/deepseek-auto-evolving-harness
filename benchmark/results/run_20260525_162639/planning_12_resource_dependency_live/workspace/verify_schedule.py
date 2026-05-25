import json

# 任务定义
tasks = {
    'A': {'duration': 2, 'cpu': 2, 'mem': 4, 'deps': []},
    'B': {'duration': 2, 'cpu': 1, 'mem': 2, 'deps': []},
    'C': {'duration': 3, 'cpu': 3, 'mem': 4, 'deps': ['A']},
    'D': {'duration': 2, 'cpu': 2, 'mem': 3, 'deps': ['A']},
    'E': {'duration': 4, 'cpu': 4, 'mem': 6, 'deps': ['B', 'C']},
    'F': {'duration': 3, 'cpu': 3, 'mem': 4, 'deps': ['D']},
    'G': {'duration': 5, 'cpu': 5, 'mem': 8, 'deps': ['E', 'F']},
    'H': {'duration': 1, 'cpu': 1, 'mem': 2, 'deps': ['E']},
    'I': {'duration': 2, 'cpu': 2, 'mem': 2, 'deps': ['G', 'H']}
}

CPU_LIMIT = 8
MEM_LIMIT = 16

def verify_schedule(schedule):
    """验证调度是否满足所有约束"""
    # 1. 检查是否包含所有任务
    scheduled_tasks = {item['task'] for item in schedule}
    all_tasks = set(tasks.keys())
    if scheduled_tasks != all_tasks:
        print(f"Missing tasks: {all_tasks - scheduled_tasks}")
        return False
    
    # 2. 检查依赖关系
    task_end_times = {item['task']: item['end'] for item in schedule}
    task_start_times = {item['task']: item['start'] for item in schedule}
    
    for item in schedule:
        task = item['task']
        start = item['start']
        for dep in tasks[task]['deps']:
            if dep not in task_end_times:
                print(f"Dependency {dep} of {task} not scheduled")
                return False
            if task_end_times[dep] > start:
                print(f"Dependency violation: {dep} ends at {task_end_times[dep]}, but {task} starts at {start}")
                return False
    
    # 3. 检查资源约束
    makespan = max(item['end'] for item in schedule)
    
    for t in range(makespan):
        cpu_used = 0
        mem_used = 0
        
        for item in schedule:
            if item['start'] <= t < item['end']:
                cpu_used += tasks[item['task']]['cpu']
                mem_used += tasks[item['task']]['mem']
        
        if cpu_used > CPU_LIMIT:
            print(f"CPU limit exceeded at time {t}: {cpu_used} > {CPU_LIMIT}")
            return False
        if mem_used > MEM_LIMIT:
            print(f"Memory limit exceeded at time {t}: {mem_used} > {MEM_LIMIT}")
            return False
    
    # 4. 检查任务持续时间
    for item in schedule:
        task = item['task']
        duration = item['end'] - item['start']
        if duration != tasks[task]['duration']:
            print(f"Task {task} has wrong duration: {duration} != {tasks[task]['duration']}")
            return False
    
    return True

def analyze_critical_path(schedule):
    """分析关键路径"""
    task_end_times = {item['task']: item['end'] for item in schedule}
    task_start_times = {item['task']: item['start'] for item in schedule}
    
    # 计算总浮动时间
    makespan = max(task_end_times.values())
    
    # 计算最早开始/结束时间（不考虑资源）
    earliest_start = {}
    earliest_finish = {}
    
    # 拓扑排序
    sorted_tasks = []
    remaining = set(tasks.keys())
    
    while remaining:
        for task in list(remaining):
            deps = tasks[task]['deps']
            if all(dep not in remaining for dep in deps):
                sorted_tasks.append(task)
                remaining.remove(task)
    
    # 计算最早时间
    for task in sorted_tasks:
        if not tasks[task]['deps']:
            earliest_start[task] = 0
        else:
            earliest_start[task] = max(earliest_finish[dep] for dep in tasks[task]['deps'])
        earliest_finish[task] = earliest_start[task] + tasks[task]['duration']
    
    # 计算最晚时间
    latest_finish = {}
    latest_start = {}
    
    for task in reversed(sorted_tasks):
        if task_end_times[task] == makespan:
            latest_finish[task] = makespan
        else:
            # 找出后继任务
            successors = [t for t in tasks.keys() if task in tasks[t]['deps']]
            if successors:
                latest_finish[task] = min(latest_start[s] for s in successors)
            else:
                latest_finish[task] = makespan
        latest_start[task] = latest_finish[task] - tasks[task]['duration']
    
    # 计算浮动时间
    total_float = {}
    for task in tasks.keys():
        total_float[task] = latest_start[task] - earliest_start[task]
    
    # 关键路径上的任务（浮动时间为0）
    critical_tasks = [task for task, tf in total_float.items() if tf == 0]
    
    # 按依赖关系排序关键任务
    critical_path = []
    for task in sorted_tasks:
        if task in critical_tasks:
            critical_path.append(task)
    
    return critical_path, total_float

# 读取生成的调度
with open('resource_schedule.json', 'r') as f:
    data = json.load(f)

schedule = data['schedule']

print("Verifying schedule...")
if verify_schedule(schedule):
    print("✓ Schedule is valid")
else:
    print("✗ Schedule is invalid")

print("\nAnalyzing critical path...")
critical_path, total_float = analyze_critical_path(schedule)
print(f"Critical path: {critical_path}")
print("\nTotal float for each task:")
for task in sorted(total_float.keys()):
    print(f"  {task}: {total_float[task]}")

# 检查是否有改进空间
print("\nChecking for potential improvements...")

# 计算理论最短工期（不考虑资源）
theoretical_makespan = 0
for task in critical_path:
    theoretical_makespan += tasks[task]['duration']
print(f"Theoretical minimum makespan (no resource constraints): {theoretical_makespan}")

# 检查是否有任务可以更早开始
for item in schedule:
    task = item['task']
    start = item['start']
    deps = tasks[task]['deps']
    
    if deps:
        latest_dep_end = max(data['schedule'][i]['end'] for i in range(len(data['schedule'])) 
                            if data['schedule'][i]['task'] in deps)
        if start > latest_dep_end:
            print(f"Task {task} could start earlier (dep ends at {latest_dep_end}, starts at {start})")

print("\nResource usage analysis:")
# 分析每个时间点的资源使用
makespan = data['makespan']
max_cpu = 0
max_mem = 0

for t in range(makespan):
    cpu_used = 0
    mem_used = 0
    
    for item in schedule:
        if item['start'] <= t < item['end']:
            cpu_used += tasks[item['task']]['cpu']
            mem_used += tasks[item['task']]['mem']
    
    max_cpu = max(max_cpu, cpu_used)
    max_mem = max(max_mem, mem_used)
    
print(f"Maximum CPU used: {max_cpu}/{CPU_LIMIT}")
print(f"Maximum Memory used: {max_mem}/{MEM_LIMIT}")