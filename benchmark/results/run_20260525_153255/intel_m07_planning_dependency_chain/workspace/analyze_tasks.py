import json
from collections import defaultdict, deque

# 读取任务数据
with open('tasks.json', 'r') as f:
    data = json.load(f)

tasks = data['tasks']

# 构建图结构
task_dict = {task['id']: task for task in tasks}
adjacency = defaultdict(list)
indegree = defaultdict(int)

for task in tasks:
    task_id = task['id']
    depends_on = task['depends_on']
    indegree[task_id] = len(depends_on)
    for dep in depends_on:
        adjacency[dep].append(task_id)

# 1) 拓扑排序
def topological_sort():
    indegree_copy = indegree.copy()
    queue = deque([task_id for task_id in indegree_copy if indegree_copy[task_id] == 0])
    result = []
    
    while queue:
        current = queue.popleft()
        result.append(current)
        
        for neighbor in adjacency[current]:
            indegree_copy[neighbor] -= 1
            if indegree_copy[neighbor] == 0:
                queue.append(neighbor)
    
    # 检查是否有循环依赖
    has_cycle = len(result) != len(tasks)
    return result, has_cycle

# 2) 计算最早开始时间和关键路径
def compute_earliest_start_and_critical_path(topological_order):
    earliest_start = {task_id: 0 for task_id in topological_order}
    earliest_finish = {task_id: 0 for task_id in topological_order}
    
    # 正向计算最早开始和完成时间
    for task_id in topological_order:
        task = task_dict[task_id]
        duration = task['duration_minutes']
        
        # 如果没有依赖，最早开始时间为0
        if not task['depends_on']:
            earliest_start[task_id] = 0
        else:
            # 最早开始时间是所有前置任务完成时间的最大值
            max_finish = 0
            for dep in task['depends_on']:
                finish_time = earliest_finish[dep]
                if finish_time > max_finish:
                    max_finish = finish_time
            earliest_start[task_id] = max_finish
        
        earliest_finish[task_id] = earliest_start[task_id] + duration
    
    # 计算项目总时长
    project_duration = max(earliest_finish.values())
    
    # 反向计算最晚开始时间，找出关键路径
    latest_start = {task_id: project_duration for task_id in topological_order}
    latest_finish = {task_id: project_duration for task_id in topological_order}
    
    # 按逆拓扑序计算
    for task_id in reversed(topological_order):
        task = task_dict[task_id]
        duration = task['duration_minutes']
        
        # 找出所有后继任务
        successors = [succ for succ in topological_order if task_id in task_dict[succ]['depends_on']]
        
        if not successors:
            # 如果没有后继任务，最晚完成时间就是项目总时长
            latest_finish[task_id] = project_duration
        else:
            # 最晚完成时间是所有后继任务最晚开始时间的最小值
            min_start = project_duration
            for succ in successors:
                if latest_start[succ] < min_start:
                    min_start = latest_start[succ]
            latest_finish[task_id] = min_start
        
        latest_start[task_id] = latest_finish[task_id] - duration
    
    # 找出关键路径任务（最早开始时间 = 最晚开始时间）
    critical_path_tasks = []
    for task_id in topological_order:
        if earliest_start[task_id] == latest_start[task_id]:
            critical_path_tasks.append(task_id)
    
    # 确保关键路径是连续的依赖链
    # 从最后一个关键任务开始向前追溯
    final_critical_path = []
    if critical_path_tasks:
        # 找到项目结束时间最晚的关键任务
        end_task = None
        max_finish = -1
        for task_id in critical_path_tasks:
            if earliest_finish[task_id] > max_finish:
                max_finish = earliest_finish[task_id]
                end_task = task_id
        
        # 从结束任务向前追溯
        current = end_task
        while current:
            final_critical_path.insert(0, current)
            
            # 找到前一个关键任务（必须是依赖关系中的）
            task = task_dict[current]
            prev_critical = None
            for dep in task['depends_on']:
                if dep in critical_path_tasks and earliest_finish[dep] == earliest_start[current]:
                    prev_critical = dep
                    break
            
            current = prev_critical
    
    critical_path_duration = sum(task_dict[task_id]['duration_minutes'] for task_id in final_critical_path)
    
    return earliest_start, earliest_finish, final_critical_path, critical_path_duration, project_duration

# 3) 计算并行分组（按最早可执行层级）
def compute_parallel_groups(topological_order, earliest_start):
    # 按最早开始时间分组
    groups_dict = defaultdict(list)
    for task_id in topological_order:
        start_time = earliest_start[task_id]
        groups_dict[start_time].append(task_id)
    
    # 将分组按开始时间排序
    sorted_times = sorted(groups_dict.keys())
    parallel_groups = [groups_dict[time] for time in sorted_times]
    
    return parallel_groups

# 执行计算
topological_order, has_cycle = topological_sort()
if has_cycle:
    print("存在循环依赖！")
else:
    earliest_start, earliest_finish, critical_path, critical_duration, project_duration = compute_earliest_start_and_critical_path(topological_order)
    parallel_groups = compute_parallel_groups(topological_order, earliest_start)
    
    # 输出结果
    result = {
        "execution_order": topological_order,
        "critical_path_task_ids": critical_path,
        "critical_path_minutes": critical_duration,
        "has_cycle": has_cycle,
        "parallel_groups": parallel_groups,
        "earliest_start_minutes": earliest_start
    }
    
    print("执行顺序:", topological_order)
    print("关键路径:", critical_path)
    print("关键路径时长:", critical_duration, "分钟")
    print("并行分组:", parallel_groups)
    print("最早开始时间:", earliest_start)
    
    # 保存到文件
    with open('execution_plan.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n结果已保存到 execution_plan.json")
