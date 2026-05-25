import json
from collections import defaultdict, deque

def read_tasks(filename):
    """读取任务数据"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['tasks']

def detect_cycle(tasks):
    """检测是否存在循环依赖"""
    # 构建邻接表
    adj = {task['id']: [] for task in tasks}
    for task in tasks:
        for dep in task['depends_on']:
            adj[dep].append(task['id'])
    
    # 构建入度表
    in_degree = {task['id']: 0 for task in tasks}
    for task in tasks:
        for dep in task['depends_on']:
            in_degree[task['id']] += 1
    
    # 使用 Kahn 算法检测环
    queue = deque([task_id for task_id, deg in in_degree.items() if deg == 0])
    visited = 0
    order = []
    
    while queue:
        node = queue.popleft()
        order.append(node)
        visited += 1
        
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return visited != len(tasks), order

def topological_sort(tasks, order):
    """根据拓扑顺序排序任务"""
    task_dict = {task['id']: task for task in tasks}
    sorted_tasks = []
    for task_id in order:
        if task_id in task_dict:
            sorted_tasks.append(task_dict[task_id])
    return sorted_tasks

def calculate_earliest_start(tasks):
    """计算最早开始时间"""
    # 构建依赖关系
    dependencies = {task['id']: task['depends_on'] for task in tasks}
    duration = {task['id']: task['duration_minutes'] for task in tasks}
    
    # 最早开始时间
    earliest_start = {}
    
    # 按拓扑顺序计算
    visited_order = []
    task_dict = {task['id']: task for task in tasks}
    
    # 首先获取拓扑顺序
    has_cycle, order = detect_cycle(tasks)
    
    for task_id in order:
        task = task_dict[task_id]
        if not task['depends_on']:
            earliest_start[task_id] = 0
        else:
            max_finish_time = 0
            for dep in task['depends_on']:
                dep_finish_time = earliest_start.get(dep, 0) + duration.get(dep, 0)
                if dep_finish_time > max_finish_time:
                    max_finish_time = dep_finish_time
            earliest_start[task_id] = max_finish_time
    
    return earliest_start, order

def calculate_critical_path(tasks, earliest_start):
    """计算关键路径"""
    # 构建依赖关系
    dependencies = {task['id']: task['depends_on'] for task in tasks}
    duration = {task['id']: task['duration_minutes'] for task in tasks}
    
    # 计算最晚开始时间和时差
    # 首先计算项目总时长
    task_ids = [task['id'] for task in tasks]
    finish_times = {task_id: earliest_start[task_id] + duration[task_id] for task_id in task_ids}
    project_duration = max(finish_times.values())
    
    # 最晚开始时间
    latest_start = {}
    # 逆拓扑顺序计算
    has_cycle, order = detect_cycle(tasks)
    reverse_order = list(reversed(order))
    
    for task_id in reverse_order:
        # 找到该任务的后继任务
        successors = []
        for task in tasks:
            if task_id in task['depends_on']:
                successors.append(task['id'])
        
        if not successors:
            # 没有后继任务，最晚开始时间 = 项目总时长 - 任务时长
            latest_start[task_id] = project_duration - duration[task_id]
        else:
            # 有后继任务，最晚开始时间 = min(后继任务的最晚开始时间) - 任务时长
            min_successor_start = min(latest_start.get(succ, project_duration) for succ in successors)
            latest_start[task_id] = min_successor_start - duration[task_id]
    
    # 计算时差
    slack = {task_id: latest_start[task_id] - earliest_start[task_id] for task_id in task_ids}
    
    # 找出关键路径（时差为0的任务）
    critical_tasks = [task_id for task_id in task_ids if slack[task_id] == 0]
    
    # 按依赖关系排序关键任务
    critical_path = []
    visited = set()
    
    def add_to_path(task_id):
        if task_id in visited:
            return
        visited.add(task_id)
        
        # 先添加依赖
        for dep in dependencies[task_id]:
            if dep in critical_tasks:
                add_to_path(dep)
        
        # 然后添加当前任务
        if task_id not in critical_path:
            critical_path.append(task_id)
    
    # 从结束任务开始
    end_tasks = [task_id for task_id in task_ids if not any(task_id in dependencies[tid] for tid in task_ids)]
    for end_task in end_tasks:
        if end_task in critical_tasks:
            add_to_path(end_task)
    
    # 确保所有关键任务都在路径中
    for task_id in critical_tasks:
        if task_id not in critical_path:
            add_to_path(task_id)
    
    # 计算关键路径总时长
    critical_path_duration = sum(duration[task_id] for task_id in critical_path)
    
    return critical_path, critical_path_duration

def group_parallel_tasks(tasks, earliest_start):
    """按最早开始时间分组并行任务"""
    # 按最早开始时间分组
    start_time_groups = defaultdict(list)
    for task in tasks:
        start_time = earliest_start[task['id']]
        start_time_groups[start_time].append(task['id'])
    
    # 将分组转换为列表并按开始时间排序
    parallel_groups = []
    for start_time in sorted(start_time_groups.keys()):
        parallel_groups.append(sorted(start_time_groups[start_time]))
    
    return parallel_groups

def main():
    # 读取任务
    tasks = read_tasks('tasks.json')
    
    # 检测循环依赖
    has_cycle, order = detect_cycle(tasks)
    
    # 计算最早开始时间
    earliest_start, order = calculate_earliest_start(tasks)
    
    # 计算关键路径
    critical_path, critical_path_duration = calculate_critical_path(tasks, earliest_start)
    
    # 分组并行任务
    parallel_groups = group_parallel_tasks(tasks, earliest_start)
    
    # 创建结果字典
    result = {
        "execution_order": order,
        "critical_path_task_ids": critical_path,
        "critical_path_minutes": critical_path_duration,
        "has_cycle": has_cycle,
        "parallel_groups": parallel_groups,
        "earliest_start_minutes": earliest_start
    }
    
    # 写入文件
    with open('execution_plan.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("执行计划已保存到 execution_plan.json")
    print(f"拓扑排序: {order}")
    print(f"关键路径: {critical_path}")
    print(f"关键路径时长: {critical_path_duration} 分钟")
    print(f"存在循环依赖: {has_cycle}")
    print(f"并行分组: {parallel_groups}")
    print(f"最早开始时间: {earliest_start}")

if __name__ == "__main__":
    main()