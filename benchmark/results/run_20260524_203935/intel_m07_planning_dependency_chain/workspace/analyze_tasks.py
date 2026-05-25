#!/usr/bin/env python3
import json
from collections import defaultdict, deque

# 读取任务数据
with open('tasks.json', 'r') as f:
    data = json.load(f)
    tasks = data['tasks']

# 创建任务字典
task_dict = {task['id']: task for task in tasks}

# 构建邻接表和入度
adj = defaultdict(list)
reverse_adj = defaultdict(list)
in_degree = defaultdict(int)

for task in tasks:
    task_id = task['id']
    in_degree[task_id] = 0

for task in tasks:
    task_id = task['id']
    for dep in task['depends_on']:
        adj[dep].append(task_id)  # dep -> task_id
        reverse_adj[task_id].append(dep)  # task_id <- dep
        in_degree[task_id] += 1

# 1) 检测循环依赖
has_cycle = False
# 使用 Kahn 算法检测循环
in_degree_copy = in_degree.copy()
queue = deque([node for node in in_degree_copy if in_degree_copy[node] == 0])
topological_order = []

while queue:
    node = queue.popleft()
    topological_order.append(node)
    for neighbor in adj[node]:
        in_degree_copy[neighbor] -= 1
        if in_degree_copy[neighbor] == 0:
            queue.append(neighbor)

if len(topological_order) != len(tasks):
    has_cycle = True
    print("发现循环依赖！")

# 2) 计算最早开始时间（如果没有循环依赖）
if not has_cycle:
    # 拓扑排序（重新计算以确保顺序）
    in_degree_copy = in_degree.copy()
    queue = deque([node for node in in_degree_copy if in_degree_copy[node] == 0])
    topological_order = []
    
    while queue:
        node = queue.popleft()
        topological_order.append(node)
        for neighbor in adj[node]:
            in_degree_copy[neighbor] -= 1
            if in_degree_copy[neighbor] == 0:
                queue.append(neighbor)
    
    # 计算最早开始时间
    earliest_start = {task_id: 0 for task_id in task_dict}
    
    for task_id in topological_order:
        max_dep_finish = 0
        for dep in reverse_adj[task_id]:
            dep_finish = earliest_start[dep] + task_dict[dep]['duration_minutes']
            if dep_finish > max_dep_finish:
                max_dep_finish = dep_finish
        earliest_start[task_id] = max_dep_finish
    
    # 3) 计算最晚开始时间和关键路径
    # 首先计算项目总时长
    total_duration = 0
    finish_times = {}
    for task_id in topological_order:
        finish_time = earliest_start[task_id] + task_dict[task_id]['duration_minutes']
        finish_times[task_id] = finish_time
        if finish_time > total_duration:
            total_duration = finish_time
    
    # 计算最晚开始时间
    latest_start = {task_id: total_duration for task_id in task_dict}
    latest_finish = {task_id: total_duration for task_id in task_dict}
    
    # 逆拓扑排序
    for task_id in reversed(topological_order):
        # 对于没有后续任务的任务，最晚完成时间等于最早完成时间
        if task_id not in adj or not adj[task_id]:
            latest_finish[task_id] = finish_times[task_id]
        else:
            # 取所有后续任务的最晚开始时间的最小值
            min_latest_start = min(latest_start[neighbor] for neighbor in adj[task_id])
            latest_finish[task_id] = min_latest_start
        
        latest_start[task_id] = latest_finish[task_id] - task_dict[task_id]['duration_minutes']
    
    # 找出关键路径上的任务
    critical_path_tasks = []
    for task_id in topological_order:
        if earliest_start[task_id] == latest_start[task_id]:
            critical_path_tasks.append(task_id)
    
    # 提取关键路径（最长依赖链）
    # 找出所有入度为0的任务作为起点
    start_tasks = [task_id for task_id in topological_order if in_degree[task_id] == 0]
    
    # 使用全局变量来跟踪最长路径
    longest_path = []
    max_length = 0
    
    def dfs(current_path, current_duration):
        nonlocal longest_path, max_length
        current_task = current_path[-1]
        
        # 检查是否是关键任务
        if earliest_start[current_task] != latest_start[current_task]:
            return
        
        # 更新最长路径
        if current_duration > max_length:
            max_length = current_duration
            longest_path = current_path.copy()
        
        # 探索后续任务
        for neighbor in adj[current_task]:
            if earliest_start[neighbor] == latest_start[neighbor]:
                dfs(current_path + [neighbor], current_duration + task_dict[neighbor]['duration_minutes'])
    
    for start_task in start_tasks:
        dfs([start_task], task_dict[start_task]['duration_minutes'])
    
    critical_path_ids = longest_path
    critical_path_minutes = sum(task_dict[task_id]['duration_minutes'] for task_id in critical_path_ids)
    
    # 4) 计算并行分组（按最早可执行层级）
    # 层级 = 从起点到该任务的最长路径长度（按任务数量）
    level_dict = {}
    for task_id in topological_order:
        if in_degree[task_id] == 0:
            level_dict[task_id] = 0
        else:
            max_level = -1
            for dep in reverse_adj[task_id]:
                if level_dict[dep] + 1 > max_level:
                    max_level = level_dict[dep] + 1
            level_dict[task_id] = max_level
    
    # 按层级分组
    max_level = max(level_dict.values())
    parallel_groups = []
    for level in range(max_level + 1):
        tasks_in_level = [task_id for task_id in topological_order if level_dict[task_id] == level]
        if tasks_in_level:
            parallel_groups.append(tasks_in_level)
    
    # 5) 创建执行计划
    execution_plan = {
        "execution_order": topological_order,
        "critical_path_task_ids": critical_path_ids,
        "critical_path_minutes": critical_path_minutes,
        "has_cycle": has_cycle,
        "parallel_groups": parallel_groups,
        "earliest_start_minutes": earliest_start
    }
    
    # 保存到文件
    with open('execution_plan.json', 'w') as f:
        json.dump(execution_plan, f, indent=2)
    
    print("分析完成！结果已保存到 execution_plan.json")
    print(f"拓扑排序: {topological_order}")
    print(f"关键路径: {critical_path_ids}")
    print(f"关键路径时长: {critical_path_minutes} 分钟")
    print(f"循环依赖: {has_cycle}")
    print(f"并行分组: {parallel_groups}")
    print(f"最早开始时间: {earliest_start}")
else:
    print("存在循环依赖，无法计算其他指标")
    execution_plan = {
        "execution_order": [],
        "critical_path_task_ids": [],
        "critical_path_minutes": 0,
        "has_cycle": True,
        "parallel_groups": [],
        "earliest_start_minutes": {}
    }
    
    with open('execution_plan.json', 'w') as f:
        json.dump(execution_plan, f, indent=2)
