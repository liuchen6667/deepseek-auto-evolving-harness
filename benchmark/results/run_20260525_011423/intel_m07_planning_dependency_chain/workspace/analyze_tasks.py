import json
from collections import defaultdict, deque

# 读取任务数据
with open('tasks.json', 'r') as f:
    data = json.load(f)

tasks = data['tasks']

# 构建任务字典和依赖图
task_dict = {task['id']: task for task in tasks}
task_ids = list(task_dict.keys())

# 构建邻接表和入度
adj = defaultdict(list)
reverse_adj = defaultdict(list)
indegree = {task_id: 0 for task_id in task_dict}
for task in tasks:
    for dep in task['depends_on']:
        adj[dep].append(task['id'])
        reverse_adj[task['id']].append(dep)
        indegree[task['id']] += 1

# 1) 检测循环依赖
def has_cycle_dfs():
    visited = {task_id: 0 for task_id in task_dict}  # 0: 未访问, 1: 访问中, 2: 已访问
    
    def dfs(node):
        if visited[node] == 1:
            return True
        if visited[node] == 2:
            return False
        visited[node] = 1
        for neighbor in adj.get(node, []):
            if dfs(neighbor):
                return True
        visited[node] = 2
        return False
    
    for node in task_dict:
        if visited[node] == 0:
            if dfs(node):
                return True
    return False

has_cycle = has_cycle_dfs()

# 2) 拓扑排序（如果无环）
execution_order = []
if not has_cycle:
    # Kahn's algorithm
    indegree_copy = indegree.copy()
    queue = deque([node for node in task_dict if indegree_copy[node] == 0])
    
    while queue:
        node = queue.popleft()
        execution_order.append(node)
        for neighbor in adj.get(node, []):
            indegree_copy[neighbor] -= 1
            if indegree_copy[neighbor] == 0:
                queue.append(neighbor)

# 3) 计算最早开始时间和关键路径
if not has_cycle:
    # 最早开始时间
    earliest_start = {task_id: 0 for task_id in task_dict}
    # 计算每个任务的最早完成时间
    earliest_finish = {task_id: 0 for task_id in task_dict}
    
    # 按拓扑顺序处理
    for task_id in execution_order:
        max_pre_finish = 0
        for dep in reverse_adj.get(task_id, []):
            max_pre_finish = max(max_pre_finish, earliest_finish[dep])
        earliest_start[task_id] = max_pre_finish
        earliest_finish[task_id] = max_pre_finish + task_dict[task_id]['duration_minutes']
    
    # 总项目时长
    project_duration = max(earliest_finish.values())
    
    # 最晚开始时间（用于计算关键路径）
    latest_start = {task_id: float('inf') for task_id in task_dict}
    latest_finish = {task_id: float('inf') for task_id in task_dict}
    
    # 初始化终点的最晚完成时间
    for task_id in task_dict:
        if not adj.get(task_id):  # 没有后继的任务
            latest_finish[task_id] = project_duration
            latest_start[task_id] = project_duration - task_dict[task_id]['duration_minutes']
    
    # 按逆拓扑顺序处理
    reverse_order = execution_order[::-1]
    for task_id in reverse_order:
        # 如果还没有设置最晚完成时间（非终点）
        if latest_finish[task_id] == float('inf'):
            # 取所有后继任务的最晚开始时间的最小值
            min_successor_start = float('inf')
            for successor in adj.get(task_id, []):
                min_successor_start = min(min_successor_start, latest_start[successor])
            latest_finish[task_id] = min_successor_start
            latest_start[task_id] = latest_finish[task_id] - task_dict[task_id]['duration_minutes']
        else:
            # 已经设置过（终点），只需要计算最晚开始
            latest_start[task_id] = latest_finish[task_id] - task_dict[task_id]['duration_minutes']
    
    # 计算时差和关键路径
    critical_path_ids = []
    for task_id in execution_order:
        slack = latest_start[task_id] - earliest_start[task_id]
        if slack == 0:
            critical_path_ids.append(task_id)
    
    # 从关键任务中提取一条连续的路径（最长依赖链）
    # 找到起点（没有前置关键任务或前置不在关键路径上）
    critical_path = []
    visited = set()
    
    def find_critical_chain(current, path):
        path.append(current)
        visited.add(current)
        # 查找后继关键任务
        successors = adj.get(current, [])
        critical_successors = [s for s in successors if s in critical_path_ids and s not in visited]
        
        if not critical_successors:
            return path
        
        # 如果有多个关键后继，选择最长的那条路径
        longest_path = []
        for succ in critical_successors:
            candidate = find_critical_chain(succ, path.copy())
            if len(candidate) > len(longest_path):
                longest_path = candidate
        
        return longest_path
    
    # 从没有前置关键任务的关键任务开始
    start_candidates = []
    for task_id in critical_path_ids:
        # 检查所有前置是否都不在关键路径上
        pre_all_not_critical = True
        for pre in reverse_adj.get(task_id, []):
            if pre in critical_path_ids:
                pre_all_not_critical = False
                break
        if pre_all_not_critical:
            start_candidates.append(task_id)
    
    # 如果找不到这样的起点（比如所有关键任务都有前置关键任务），取第一个关键任务
    if not start_candidates:
        start_candidates = [critical_path_ids[0]]
    
    # 从每个起点尝试，取最长路径
    final_critical_path = []
    for start in start_candidates:
        path = find_critical_chain(start, [])
        if len(path) > len(final_critical_path):
            final_critical_path = path
    
    critical_path_ids = final_critical_path
    critical_path_minutes = sum(task_dict[task_id]['duration_minutes'] for task_id in critical_path_ids)
    
    # 4) 计算并行组（按最早可执行层级分组）
    # 层级：没有依赖的任务为0级，依赖层级最大的前置任务+1
    levels = {}
    for task_id in execution_order:
        if not reverse_adj.get(task_id):  # 没有依赖
            levels[task_id] = 0
        else:
            max_level = -1
            for dep in reverse_adj[task_id]:
                max_level = max(max_level, levels[dep])
            levels[task_id] = max_level + 1
    
    # 按层级分组
    max_level = max(levels.values())
    parallel_groups = []
    for level in range(max_level + 1):
        group = [task_id for task_id in task_dict if levels[task_id] == level]
        if group:
            parallel_groups.append(group)
    
    # 5) 准备输出
    result = {
        "execution_order": execution_order,
        "critical_path_task_ids": critical_path_ids,
        "critical_path_minutes": critical_path_minutes,
        "has_cycle": has_cycle,
        "parallel_groups": parallel_groups,
        "earliest_start_minutes": earliest_start
    }
    
else:
    # 有循环依赖的情况
    result = {
        "execution_order": [],
        "critical_path_task_ids": [],
        "critical_path_minutes": 0,
        "has_cycle": True,
        "parallel_groups": [],
        "earliest_start_minutes": {}
    }

# 输出结果
print("分析结果:")
print(json.dumps(result, indent=2))

# 保存到文件
with open('execution_plan.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\n已保存到 execution_plan.json")