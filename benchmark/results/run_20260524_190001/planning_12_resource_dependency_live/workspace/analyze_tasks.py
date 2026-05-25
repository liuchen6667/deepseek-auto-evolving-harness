#!/usr/bin/env python3

tasks = {
    'A': {'duration': 2, 'cpu': 2, 'mem': 4, 'deps': []},
    'B': {'duration': 2, 'cpu': 1, 'mem': 2, 'deps': []},
    'C': {'duration': 3, 'cpu': 3, 'mem': 4, 'deps': ['A']},
    'D': {'duration': 2, 'cpu': 2, 'mem': 3, 'deps': ['A']},
    'E': {'duration': 4, 'cpu': 4, 'mem': 6, 'deps': ['B', 'C']},
    'F': {'duration': 3, 'cpu': 3, 'mem': 4, 'deps': ['D']},
    'H': {'duration': 1, 'cpu': 1, 'mem': 2, 'deps': ['E']},
    'G': {'duration': 5, 'cpu': 5, 'mem': 8, 'deps': ['E', 'F']},
    'I': {'duration': 2, 'cpu': 2, 'mem': 2, 'deps': ['G', 'H']},
}

# 资源限制
cpu_limit = 8
mem_limit = 16

print("任务依赖关系:")
for task, info in tasks.items():
    print(f"{task}: duration={info['duration']}, cpu={info['cpu']}, mem={info['mem']}, deps={info['deps']}")

print("\n关键路径分析（不考虑资源约束）:")
# 计算最早开始时间（不考虑资源）
def compute_early_times(tasks):
    early_start = {task: 0 for task in tasks}
    early_finish = {task: 0 for task in tasks}
    
    # 拓扑排序
    order = []
    visited = set()
    
    def dfs(task):
        if task in visited:
            return
        visited.add(task)
        
        for dep in tasks[task]['deps']:
            dfs(dep)
        
        order.append(task)
    
    for task in tasks:
        dfs(task)
    
    # 计算最早时间
    for task in order:
        if not tasks[task]['deps']:
            early_start[task] = 0
        else:
            early_start[task] = max(early_finish[dep] for dep in tasks[task]['deps'])
        early_finish[task] = early_start[task] + tasks[task]['duration']
    
    return early_start, early_finish, order

early_start, early_finish, order = compute_early_times(tasks)

print("最早开始和完成时间:")
for task in order:
    print(f"{task}: start={early_start[task]}, finish={early_finish[task]}")

# 计算最晚时间（不考虑资源）
def compute_late_times(tasks, early_finish):
    late_finish = {}
    late_start = {}
    
    # 反向拓扑排序
    reverse_order = list(reversed(order))
    
    # 找到最大完成时间
    makespan = max(early_finish.values())
    
    for task in reverse_order:
        # 找到后继任务
        successors = []
        for t, info in tasks.items():
            if task in info['deps']:
                successors.append(t)
        
        if not successors:
            late_finish[task] = makespan
        else:
            late_finish[task] = min(late_start[s] for s in successors)
        
        late_start[task] = late_finish[task] - tasks[task]['duration']
    
    return late_start, late_finish

late_start, late_finish = compute_late_times(tasks, early_finish)

print("\n最晚开始和完成时间:")
for task in order:
    print(f"{task}: late_start={late_start[task]}, late_finish={late_finish[task]}")

print("\n关键路径任务（总时差=0）:")
critical_path = []
for task in order:
    total_float = late_start[task] - early_start[task]
    if total_float == 0:
        critical_path.append(task)
        print(f"{task}: 总时差={total_float}")

print(f"\n不考虑资源约束的关键路径: {critical_path}")
print(f"不考虑资源约束的makespan: {max(early_finish.values())}")

# 资源需求分析
print("\n资源需求分析:")
for task, info in tasks.items():
    print(f"{task}: CPU需求={info['cpu']} ({info['cpu']/cpu_limit*100:.1f}%), Memory需求={info['mem']} ({info['mem']/mem_limit*100:.1f}%)")

print("\n资源密集型任务:")
for task, info in tasks.items():
    if info['cpu'] >= 4 or info['mem'] >= 6:
        print(f"{task}: cpu={info['cpu']}, mem={info['mem']}")