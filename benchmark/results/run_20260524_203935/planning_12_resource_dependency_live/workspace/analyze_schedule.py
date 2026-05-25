import json
from collections import defaultdict

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
CPU_LIMIT = 8
MEM_LIMIT = 16

# 计算关键路径（不考虑资源限制）
def calculate_critical_path():
    # 计算最早开始时间（不考虑资源）
    earliest_start = {}
    latest_finish = {}
    
    # 拓扑排序
    visited = set()
    order = []
    
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for dep in tasks[node]['deps']:
            dfs(dep)
        order.append(node)
    
    for task in tasks:
        if task not in visited:
            dfs(task)
    
    # 计算最早开始和完成时间
    earliest_finish = {}
    for task in order:
        if not tasks[task]['deps']:
            earliest_start[task] = 0
        else:
            earliest_start[task] = max(earliest_finish[dep] for dep in tasks[task]['deps'])
        earliest_finish[task] = earliest_start[task] + tasks[task]['duration']
    
    # 计算最晚开始和完成时间
    makespan = max(earliest_finish.values())
    latest_start = {}
    latest_finish = {}
    
    for task in reversed(order):
        # 找出后继任务
        successors = [t for t in tasks if task in tasks[t]['deps']]
        if not successors:
            latest_finish[task] = makespan
        else:
            latest_finish[task] = min(latest_start[s] for s in successors)
        latest_start[task] = latest_finish[task] - tasks[task]['duration']
    
    # 找出关键路径上的任务（总浮动时间为0）
    critical_path = []
    for task in order:
        total_float = latest_start[task] - earliest_start[task]
        if total_float == 0:
            critical_path.append(task)
    
    return critical_path, makespan

# 打印任务信息
print("任务信息:")
for task, info in tasks.items():
    print(f"{task}: duration={info['duration']}, cpu={info['cpu']}, mem={info['mem']}, deps={info['deps']}")

print(f"\n资源限制: CPU <= {CPU_LIMIT}, Memory <= {MEM_LIMIT}")

# 计算不考虑资源的关键路径
critical_path, theoretical_makespan = calculate_critical_path()
print(f"\n不考虑资源的关键路径: {critical_path}")
print(f"不考虑资源的最短工期: {theoretical_makespan}")

# 依赖关系图
print("\n依赖关系图:")
for task, info in tasks.items():
    if info['deps']:
        print(f"{task} 依赖于: {info['deps']}")

# 分析资源需求
print("\n资源需求分析:")
for task, info in tasks.items():
    print(f"{task}: 需要 CPU={info['cpu']}/{CPU_LIMIT} ({info['cpu']/CPU_LIMIT*100:.1f}%), "
          f"Memory={info['mem']}/{MEM_LIMIT} ({info['mem']/MEM_LIMIT*100:.1f}%)")