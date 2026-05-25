#!/usr/bin/env python3
import json
from collections import defaultdict, deque

def load_tasks():
    with open('tasks.json', 'r') as f:
        data = json.load(f)
    return data['tasks']

def check_cycle(tasks):
    """检查是否有循环依赖"""
    graph = {task['id']: [] for task in tasks}
    indegree = {task['id']: 0 for task in tasks}
    
    for task in tasks:
        for dep in task['depends_on']:
            graph[dep].append(task['id'])
            indegree[task['id']] += 1
    
    # Kahn's algorithm
    zero_indegree = deque([node for node in indegree if indegree[node] == 0])
    topo_order = []
    
    while zero_indegree:
        node = zero_indegree.popleft()
        topo_order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                zero_indegree.append(neighbor)
    
    has_cycle = len(topo_order) != len(tasks)
    return has_cycle, topo_order if not has_cycle else []

def compute_earliest_start(tasks, topo_order):
    """计算最早开始时间"""
    task_map = {task['id']: task for task in tasks}
    earliest_start = {task['id']: 0 for task in tasks}
    earliest_finish = {task['id']: 0 for task in tasks}
    
    for task_id in topo_order:
        task = task_map[task_id]
        max_dep_finish = 0
        for dep_id in task['depends_on']:
            max_dep_finish = max(max_dep_finish, earliest_finish[dep_id])
        earliest_start[task_id] = max_dep_finish
        earliest_finish[task_id] = max_dep_finish + task['duration_minutes']
    
    return earliest_start, earliest_finish

def compute_critical_path(tasks, topo_order, earliest_start, earliest_finish):
    """计算关键路径"""
    task_map = {task['id']: task for task in tasks}
    
    # 计算最晚开始时间
    total_duration = max(earliest_finish.values())
    latest_finish = {task['id']: total_duration for task in tasks}
    latest_start = {task['id']: total_duration for task in tasks}
    
    # 反向拓扑排序
    for task_id in reversed(topo_order):
        task = task_map[task_id]
        
        # 找到依赖此任务的所有任务
        dependents = []
        for t in tasks:
            if task_id in t['depends_on']:
                dependents.append(t['id'])
        
        if not dependents:
            # 没有后续任务，最晚完成时间等于总时长
            latest_finish[task_id] = total_duration
        else:
            # 取所有后续任务的最晚开始时间的最小值
            min_latest_start = min(latest_start[dep] for dep in dependents)
            latest_finish[task_id] = min_latest_start
        
        latest_start[task_id] = latest_finish[task_id] - task['duration_minutes']
    
    # 找出关键路径上的任务（最早开始=最晚开始）
    critical_tasks = []
    for task_id in topo_order:
        if abs(earliest_start[task_id] - latest_start[task_id]) < 0.0001:
            critical_tasks.append(task_id)
    
    # 确保关键路径是连续的依赖链
    critical_path = []
    current = None
    
    # 找到起点（没有依赖的关键任务）
    for task_id in critical_tasks:
        task = task_map[task_id]
        if not task['depends_on']:
            current = task_id
            break
    
    # 沿着依赖链构建关键路径
    while current:
        critical_path.append(current)
        
        # 找到当前任务的关键后继
        next_task = None
        for task_id in critical_tasks:
            task = task_map[task_id]
            if current in task['depends_on'] and task_id not in critical_path:
                next_task = task_id
                break
        
        current = next_task
    
    # 计算关键路径总时长
    critical_path_duration = sum(task_map[task_id]['duration_minutes'] for task_id in critical_path)
    
    return critical_path, critical_path_duration

def group_parallel_tasks(tasks, earliest_start):
    """按最早开始时间分组并行任务"""
    # 按最早开始时间分组
    groups = defaultdict(list)
    for task in tasks:
        groups[earliest_start[task['id']]].append(task['id'])
    
    # 按开始时间排序并转换为列表
    sorted_groups = []
    for start_time in sorted(groups.keys()):
        sorted_groups.append(groups[start_time])
    
    return sorted_groups

def main():
    tasks = load_tasks()
    
    # 检查循环依赖并获取拓扑排序
    has_cycle, topo_order = check_cycle(tasks)
    
    if has_cycle:
        print("发现循环依赖！")
        result = {
            "execution_order": [],
            "critical_path_task_ids": [],
            "critical_path_minutes": 0,
            "has_cycle": True,
            "parallel_groups": [],
            "earliest_start_minutes": {}
        }
    else:
        # 计算最早开始时间
        earliest_start, earliest_finish = compute_earliest_start(tasks, topo_order)
        
        # 计算关键路径
        critical_path, critical_path_duration = compute_critical_path(tasks, topo_order, earliest_start, earliest_finish)
        
        # 分组并行任务
        parallel_groups = group_parallel_tasks(tasks, earliest_start)
        
        result = {
            "execution_order": topo_order,
            "critical_path_task_ids": critical_path,
            "critical_path_minutes": critical_path_duration,
            "has_cycle": False,
            "parallel_groups": parallel_groups,
            "earliest_start_minutes": earliest_start
        }
    
    # 保存结果
    with open('execution_plan.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("分析完成！结果已保存到 execution_plan.json")
    print(f"拓扑排序: {result['execution_order']}")
    print(f"关键路径: {result['critical_path_task_ids']} (总时长: {result['critical_path_minutes']} 分钟)")
    print(f"循环依赖: {result['has_cycle']}")
    
if __name__ == "__main__":
    main()