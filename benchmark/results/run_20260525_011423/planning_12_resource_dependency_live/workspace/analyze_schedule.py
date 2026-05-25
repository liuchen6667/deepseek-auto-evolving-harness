#!/usr/bin/env python3
"""
资源受限项目调度问题（RCPSP）分析
任务：A-I，资源限制：CPU <= 8, Memory <= 16
目标：最小化makespan
"""

# 任务数据
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

# 资源限制
resource_limits = {'cpu': 8, 'mem': 16}

# 计算关键路径（无资源约束）
def compute_earliest_start_times():
    """计算最早开始时间（忽略资源约束）"""
    earliest_start = {task: 0 for task in tasks}
    
    # 拓扑排序（基于依赖关系）
    visited = set()
    
    def dfs(task):
        if task in visited:
            return earliest_start[task]
        
        max_dep_time = 0
        for dep in tasks[task]['deps']:
            dep_time = dfs(dep)
            max_dep_time = max(max_dep_time, dep_time + tasks[dep]['duration'])
        
        earliest_start[task] = max_dep_time
        visited.add(task)
        return max_dep_time
    
    for task in tasks:
        dfs(task)
    
    return earliest_start

def compute_latest_start_times(earliest_start):
    """计算最晚开始时间（忽略资源约束）"""
    # 首先计算项目总时长
    makespan = max(earliest_start[task] + tasks[task]['duration'] for task in tasks)
    
    latest_start = {}
    # 从后往前计算
    # 按依赖反向传播
    reverse_deps = {task: [] for task in tasks}
    for task, data in tasks.items():
        for dep in data['deps']:
            reverse_deps[dep].append(task)
    
    # 初始化最晚完成时间为makespan
    latest_finish = {task: makespan for task in tasks}
    
    # 计算最晚开始时间
    for task in tasks:
        # 任务的最晚开始时间 = 最晚完成时间 - 持续时间
        latest_start[task] = latest_finish[task] - tasks[task]['duration']
        
        # 对于依赖它的任务，更新它们的最晚完成时间
        for dep in tasks[task]['deps']:
            # 依赖任务的最晚完成时间不能晚于当前任务的最晚开始时间
            latest_finish[dep] = min(latest_finish.get(dep, makespan), latest_start[task])
    
    # 重新计算以确保一致性
    for task in list(tasks.keys())[::-1]:
        # 如果没有后继任务，最晚完成时间 = makespan
        if not reverse_deps[task]:
            latest_finish[task] = makespan
        else:
            # 后继任务的最早开始时间的最小值
            min_successor_start = min(latest_start.get(succ, makespan) for succ in reverse_deps[task])
            latest_finish[task] = min_successor_start
        
        latest_start[task] = latest_finish[task] - tasks[task]['duration']
    
    return latest_start, makespan

def find_critical_path(earliest_start, latest_start):
    """找到关键路径"""
    critical_path = []
    
    # 找出最早开始时间等于最晚开始时间的任务
    for task in tasks:
        if earliest_start[task] == latest_start[task]:
            critical_path.append(task)
    
    # 按开始时间排序
    critical_path.sort(key=lambda x: earliest_start[x])
    
    return critical_path

# 计算最早和最晚开始时间
earliest_start = compute_earliest_start_times()
latest_start, makespan_no_resource = compute_latest_start_times(earliest_start)
critical_path = find_critical_path(earliest_start, latest_start)

print("=== 无资源约束分析 ===")
print(f"最早开始时间: {earliest_start}")
print(f"最晚开始时间: {latest_start}")
print(f"关键路径（无资源约束）: {' -> '.join(critical_path)}")
print(f"项目总时长（无资源约束）: {makespan_no_resource}")

print("\n=== 任务依赖关系 ===")
for task, data in tasks.items():
    print(f"{task}: duration={data['duration']}, cpu={data['cpu']}, mem={data['mem']}, deps={data['deps']}")

print("\n=== 资源需求分析 ===")
# 分析并行执行时的峰值资源需求
time_points = set()
for task in tasks:
    time_points.add(earliest_start[task])
    time_points.add(earliest_start[task] + tasks[task]['duration'])

time_points = sorted(time_points)
print("时间点:", time_points)

# 检查每个时间点的资源需求
for t in time_points:
    cpu_usage = 0
    mem_usage = 0
    active_tasks = []
    
    for task in tasks:
        start = earliest_start[task]
        end = start + tasks[task]['duration']
        if start <= t < end:
            cpu_usage += tasks[task]['cpu']
            mem_usage += tasks[task]['mem']
            active_tasks.append(task)
    
    print(f"时间 {t}: CPU={cpu_usage}, Memory={mem_usage}, 活动任务: {active_tasks}")