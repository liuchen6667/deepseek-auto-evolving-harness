#!/usr/bin/env python3

tasks = {
    'A': {'dur': 2, 'cpu': 2, 'mem': 4, 'deps': []},
    'B': {'dur': 2, 'cpu': 1, 'mem': 2, 'deps': []},
    'C': {'dur': 3, 'cpu': 3, 'mem': 4, 'deps': ['A']},
    'D': {'dur': 2, 'cpu': 2, 'mem': 3, 'deps': ['A']},
    'E': {'dur': 4, 'cpu': 4, 'mem': 6, 'deps': ['B', 'C']},
    'F': {'dur': 3, 'cpu': 3, 'mem': 4, 'deps': ['D']},
    'G': {'dur': 5, 'cpu': 5, 'mem': 8, 'deps': ['E', 'F']},
    'H': {'dur': 1, 'cpu': 1, 'mem': 2, 'deps': ['E']},
    'I': {'dur': 2, 'cpu': 2, 'mem': 2, 'deps': ['G', 'H']}
}

cpu_limit = 8
mem_limit = 16

def compute_earliest_start(tasks):
    """计算不考虑资源约束的最早开始时间"""
    earliest_start = {}
    
    # 拓扑排序
    remaining = set(tasks.keys())
    
    while remaining:
        for task in list(remaining):
            deps = tasks[task]['deps']
            if all(dep not in remaining for dep in deps):
                if not deps:
                    earliest_start[task] = 0
                else:
                    earliest_start[task] = max(earliest_start[dep] + tasks[dep]['dur'] for dep in deps)
                remaining.remove(task)
                break
    
    return earliest_start

earliest = compute_earliest_start(tasks)
print("不考虑资源约束的最早开始时间:")
for task in sorted(earliest.keys()):
    print(f"{task}: {earliest[task]}-{earliest[task]+tasks[task]['dur']}")

print("\n关键路径分析:")
# 计算最长的路径
paths = []

def find_paths(task, current_path, duration):
    current_path = current_path + [task]
    duration += tasks[task]['dur']
    
    # 找到依赖于当前任务的任务
    dependents = [t for t in tasks if task in tasks[t]['deps']]
    
    if not dependents:
        paths.append((current_path, duration))
    else:
        for dep in dependents:
            find_paths(dep, current_path, duration)

# 从没有依赖的任务开始
start_tasks = [t for t in tasks if not tasks[t]['deps']]
for task in start_tasks:
    find_paths(task, [], 0)

longest = max(paths, key=lambda x: x[1])
print(f"关键路径: {' -> '.join(longest[0])}, 长度: {longest[1]}")