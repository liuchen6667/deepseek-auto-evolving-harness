import json
from collections import defaultdict, deque

def read_tasks():
    with open('tasks.json', 'r') as f:
        data = json.load(f)
    return data['tasks']

def topological_sort(tasks):
    # 构建图
    graph = {task['id']: [] for task in tasks}
    in_degree = {task['id']: 0 for task in tasks}
    task_map = {task['id']: task for task in tasks}
    
    for task in tasks:
        for dep in task['depends_on']:
            graph[dep].append(task['id'])
            in_degree[task['id']] += 1
    
    # Kahn's 算法
    queue = deque([node for node in in_degree if in_degree[node] == 0])
    topo_order = []
    
    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # 检查是否有循环依赖
    has_cycle = len(topo_order) != len(tasks)
    
    return topo_order, has_cycle, task_map, graph

def calculate_earliest_start(topo_order, task_map, graph):
    # 反转图用于找前置任务
    reverse_graph = defaultdict(list)
    for task_id, deps in graph.items():
        for dep in deps:
            reverse_graph[dep].append(task_id)
    
    earliest_start = {}
    for task_id in topo_order:
        if task_id not in reverse_graph or not reverse_graph[task_id]:
            earliest_start[task_id] = 0
        else:
            max_time = 0
            for pred in reverse_graph[task_id]:
                pred_finish = earliest_start[pred] + task_map[pred]['duration_minutes']
                max_time = max(max_time, pred_finish)
            earliest_start[task_id] = max_time
    
    return earliest_start

def calculate_latest_start(topo_order, task_map, graph, earliest_start):
    # 反转拓扑顺序
    reverse_topo = list(reversed(topo_order))
    
    # 构建正向图用于找后续任务
    forward_graph = defaultdict(list)
    for task_id, deps in graph.items():
        for dep in deps:
            forward_graph[task_id].append(dep)
    
    # 计算项目总时长
    project_duration = 0
    for task_id in topo_order:
        finish_time = earliest_start[task_id] + task_map[task_id]['duration_minutes']
        project_duration = max(project_duration, finish_time)
    
    latest_start = {}
    latest_finish = {}
    
    # 从后向前计算
    for task_id in reverse_topo:
        if task_id not in forward_graph or not forward_graph[task_id]:
            # 没有后续任务
            latest_finish[task_id] = project_duration
            latest_start[task_id] = latest_finish[task_id] - task_map[task_id]['duration_minutes']
        else:
            # 有后续任务
            min_latest_start = float('inf')
            for succ in forward_graph[task_id]:
                min_latest_start = min(min_latest_start, latest_start[succ])
            latest_finish[task_id] = min_latest_start
            latest_start[task_id] = latest_finish[task_id] - task_map[task_id]['duration_minutes']
    
    return latest_start, project_duration

def find_critical_path(topo_order, task_map, earliest_start, latest_start):
    critical_path = []
    
    for task_id in topo_order:
        if earliest_start[task_id] == latest_start[task_id]:
            critical_path.append(task_id)
    
    return critical_path

def group_parallel_tasks(topo_order, task_map, earliest_start):
    # 按最早开始时间分组
    groups = defaultdict(list)
    for task_id in topo_order:
        groups[earliest_start[task_id]].append(task_id)
    
    # 转换为列表并按时间排序
    parallel_groups = []
    for start_time in sorted(groups.keys()):
        parallel_groups.append(groups[start_time])
    
    return parallel_groups

def main():
    tasks = read_tasks()
    topo_order, has_cycle, task_map, graph = topological_sort(tasks)
    
    if has_cycle:
        print("检测到循环依赖！")
        # 对于有循环依赖的情况，我们仍然尝试计算其他值
        earliest_start = {}
        critical_path = []
        parallel_groups = []
        project_duration = 0
    else:
        earliest_start = calculate_earliest_start(topo_order, task_map, graph)
        latest_start, project_duration = calculate_latest_start(topo_order, task_map, graph, earliest_start)
        critical_path = find_critical_path(topo_order, task_map, earliest_start, latest_start)
        parallel_groups = group_parallel_tasks(topo_order, task_map, earliest_start)
    
    # 创建结果字典
    result = {
        "execution_order": topo_order,
        "critical_path_task_ids": critical_path,
        "critical_path_minutes": project_duration,
        "has_cycle": has_cycle,
        "parallel_groups": parallel_groups,
        "earliest_start_minutes": earliest_start
    }
    
    # 写入文件
    with open('execution_plan.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("分析完成！结果已写入 execution_plan.json")
    print(f"拓扑排序: {topo_order}")
    print(f"循环依赖: {has_cycle}")
    print(f"关键路径: {critical_path}")
    print(f"关键路径时长: {project_duration} 分钟")
    print(f"并行分组: {parallel_groups}")
    print(f"最早开始时间: {earliest_start}")

if __name__ == "__main__":
    main()