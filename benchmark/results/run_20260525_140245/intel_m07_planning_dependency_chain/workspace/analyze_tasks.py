#!/usr/bin/env python3
import json
from collections import defaultdict, deque

def load_tasks():
    with open('tasks.json', 'r') as f:
        data = json.load(f)
    return data['tasks']

def topological_sort(tasks):
    # 构建邻接表和入度
    adj = defaultdict(list)
    indegree = {}
    task_map = {}
    
    for task in tasks:
        task_id = task['id']
        task_map[task_id] = task
        indegree[task_id] = 0
    
    for task in tasks:
        task_id = task['id']
        for dep in task['depends_on']:
            adj[dep].append(task_id)
            indegree[task_id] += 1
    
    # Kahn算法
    queue = deque([task_id for task_id in indegree if indegree[task_id] == 0])
    sorted_order = []
    
    while queue:
        node = queue.popleft()
        sorted_order.append(node)
        for neighbor in adj[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    
    # 检查循环依赖
    has_cycle = len(sorted_order) != len(tasks)
    return sorted_order, has_cycle, adj, task_map

def calculate_earliest_times(sorted_order, adj, task_map):
    earliest_start = {}
    earliest_finish = {}
    
    for task_id in sorted_order:
        task = task_map[task_id]
        if not task['depends_on']:
            earliest_start[task_id] = 0
        else:
            earliest_start[task_id] = max(earliest_finish[dep] for dep in task['depends_on'])
        earliest_finish[task_id] = earliest_start[task_id] + task['duration_minutes']
    
    return earliest_start, earliest_finish

def calculate_latest_times(sorted_order, adj, task_map, earliest_finish):
    latest_start = {}
    latest_finish = {}
    
    # 反向拓扑序
    reverse_order = list(reversed(sorted_order))
    
    # 初始化
    for task_id in sorted_order:
        latest_finish[task_id] = float('inf')
    
    # 项目总时长是关键路径长度
    project_duration = max(earliest_finish.values())
    
    for task_id in reverse_order:
        task = task_map[task_id]
        # 找出所有后继任务
        successors = []
        for pred, succ_list in adj.items():
            if task_id in succ_list:
                # task_id是pred的后继，所以我们需要找到所有task_id的后继
                pass
        # 更简单的方法：构建反向邻接表
        
    # 构建反向邻接表
    reverse_adj = defaultdict(list)
    for task in tasks:
        task_id = task['id']
        for dep in task['depends_on']:
            reverse_adj[task_id].append(dep)
    
    for task_id in reverse_order:
        task = task_map[task_id]
        # 如果没有后继，最晚完成时间等于项目总时长
        has_successors = False
        for pred, succ_list in adj.items():
            if task_id in succ_list:
                has_successors = True
                break
        
        if not has_successors:
            latest_finish[task_id] = project_duration
        else:
            # 找出所有直接后继的最晚开始时间的最小值
            min_latest_start = float('inf')
            for pred, succ_list in adj.items():
                if task_id in succ_list:
                    # task_id是pred的后继，所以我们需要找到task_id的所有后继
                    # 实际上我们需要构建正向邻接表来找到后继
                    pass
    
    # 简化方法：使用关键路径算法
    return latest_start, latest_finish

def find_critical_path(tasks, sorted_order, earliest_start, earliest_finish):
    # 计算项目总时长
    project_duration = max(earliest_finish.values())
    
    # 计算最晚时间
    latest_finish = {}
    latest_start = {}
    
    # 反向拓扑序
    reverse_order = list(reversed(sorted_order))
    
    # 构建反向邻接表（任务id -> 依赖它的任务）
    reverse_adj = defaultdict(list)
    for task in tasks:
        task_id = task['id']
        for dep in task['depends_on']:
            reverse_adj[dep].append(task_id)
    
    # 初始化
    for task in tasks:
        task_id = task['id']
        latest_finish[task_id] = float('inf')
    
    # 计算最晚时间
    for task_id in reverse_order:
        task = next(t for t in tasks if t['id'] == task_id)
        
        # 如果没有后继，最晚完成时间等于项目总时长
        if task_id not in reverse_adj or not reverse_adj[task_id]:
            latest_finish[task_id] = project_duration
        else:
            # 最晚完成时间 = 后继任务的最晚开始时间的最小值
            min_latest_start = float('inf')
            for succ in reverse_adj[task_id]:
                if latest_start[succ] < min_latest_start:
                    min_latest_start = latest_start[succ]
            latest_finish[task_id] = min_latest_start
        
        latest_start[task_id] = latest_finish[task_id] - task['duration_minutes']
    
    # 找出关键路径：最早开始=最晚开始 且 最早完成=最晚完成的任务
    critical_path = []
    for task_id in sorted_order:
        if earliest_start[task_id] == latest_start[task_id] and earliest_finish[task_id] == latest_finish[task_id]:
            critical_path.append(task_id)
    
    # 确保关键路径是连续的依赖链
    # 从最后一个关键任务开始向前追溯
    if critical_path:
        # 找到最终的关键任务（没有关键后继）
        final_critical = None
        for task_id in critical_path:
            has_critical_successor = False
            for succ in reverse_adj[task_id]:
                if succ in critical_path:
                    has_critical_successor = True
                    break
            if not has_critical_successor:
                final_critical = task_id
                break
        
        # 从最终任务向前构建连续链
        continuous_path = []
        current = final_critical
        while current:
            continuous_path.insert(0, current)
            # 找到前驱关键任务
            task = next(t for t in tasks if t['id'] == current)
            pred_critical = None
            for dep in task['depends_on']:
                if dep in critical_path:
                    pred_critical = dep
                    break
            current = pred_critical
        
        critical_path = continuous_path
    
    return critical_path, project_duration

def find_parallel_groups(sorted_order, earliest_start):
    # 按最早开始时间分组
    groups = defaultdict(list)
    for task_id in sorted_order:
        groups[earliest_start[task_id]].append(task_id)
    
    # 转换为列表并按开始时间排序
    parallel_groups = []
    for start_time in sorted(groups.keys()):
        parallel_groups.append(groups[start_time])
    
    return parallel_groups

def main():
    tasks = load_tasks()
    
    # 拓扑排序
    sorted_order, has_cycle, adj, task_map = topological_sort(tasks)
    
    # 计算最早时间
    earliest_start, earliest_finish = calculate_earliest_times(sorted_order, adj, task_map)
    
    # 找到关键路径
    critical_path, critical_path_minutes = find_critical_path(tasks, sorted_order, earliest_start, earliest_finish)
    
    # 找到并行组
    parallel_groups = find_parallel_groups(sorted_order, earliest_start)
    
    # 创建结果
    result = {
        "execution_order": sorted_order,
        "critical_path_task_ids": critical_path,
        "critical_path_minutes": critical_path_minutes,
        "has_cycle": has_cycle,
        "parallel_groups": parallel_groups,
        "earliest_start_minutes": earliest_start
    }
    
    # 保存结果
    with open('execution_plan.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # 打印结果
    print("拓扑排序执行顺序:", sorted_order)
    print("关键路径任务ID:", critical_path)
    print("关键路径时长:", critical_path_minutes, "分钟")
    print("是否存在循环依赖:", has_cycle)
    print("并行组:", parallel_groups)
    print("最早开始时间:", earliest_start)

if __name__ == "__main__":
    main()