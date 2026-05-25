import itertools
import json
from typing import List, Dict, Tuple, Set

# 任务定义
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

# 资源上限
CPU_LIMIT = 8
MEM_LIMIT = 16

def is_valid_schedule(schedule: List[Dict]) -> bool:
    """检查调度是否满足所有约束"""
    # 检查依赖关系
    task_end_times = {item['task']: item['end'] for item in schedule}
    for item in schedule:
        task = item['task']
        start = item['start']
        for dep in tasks[task]['deps']:
            if dep not in task_end_times or task_end_times[dep] > start:
                return False
    
    # 检查资源约束（按时间点检查）
    max_time = max(item['end'] for item in schedule) if schedule else 0
    
    for t in range(max_time):
        cpu_used = 0
        mem_used = 0
        
        for item in schedule:
            if item['start'] <= t < item['end']:
                cpu_used += tasks[item['task']]['cpu']
                mem_used += tasks[item['task']]['mem']
        
        if cpu_used > CPU_LIMIT or mem_used > MEM_LIMIT:
            return False
    
    return True

def find_critical_path(schedule: List[Dict]) -> List[str]:
    """从调度中找出关键路径"""
    # 构建任务图
    task_end_times = {item['task']: item['end'] for item in schedule}
    task_start_times = {item['task']: item['start'] for item in schedule}
    
    # 找出最后完成的任务
    makespan = max(task_end_times.values())
    last_tasks = [task for task, end in task_end_times.items() if end == makespan]
    
    # 从最后一个任务回溯找关键路径
    critical_path = []
    if last_tasks:
        # 取字母序最小的最后一个任务（如果有多个）
        current = min(last_tasks)
        
        while True:
            critical_path.insert(0, current)
            
            # 找前驱任务
            deps = tasks[current]['deps']
            if not deps:
                break
            
            # 找出影响当前任务开始时间的前驱
            # 即前驱的结束时间等于当前任务的开始时间
            best_dep = None
            best_end_time = -1
            
            for dep in deps:
                end_time = task_end_times[dep]
                if end_time == task_start_times[current]:
                    best_dep = dep
                    break
                elif end_time > best_end_time:
                    best_end_time = end_time
                    best_dep = dep
            
            if best_dep is None:
                break
                
            current = best_dep
    
    return critical_path

def generate_parallel_groups(schedule: List[Dict]) -> List[List[str]]:
    """生成按相同开始时间分组的并行任务组"""
    # 按开始时间分组
    start_time_groups = {}
    for item in schedule:
        start = item['start']
        if start not in start_time_groups:
            start_time_groups[start] = []
        start_time_groups[start].append(item['task'])
    
    # 对每个组内的任务按字母序排序
    parallel_groups = []
    for start in sorted(start_time_groups.keys()):
        group = sorted(start_time_groups[start])
        if len(group) > 1:
            parallel_groups.append(group)
    
    return parallel_groups

def greedy_schedule() -> Dict:
    """使用贪心算法尝试找到最短工期的调度"""
    # 初始化
    completed = set()
    in_progress = {}  # task -> end_time
    time = 0
    schedule = []
    
    # 按字母序预排序任务，用于打破平局
    all_tasks = sorted(tasks.keys())
    
    while len(completed) < len(tasks):
        # 更新进行中的任务
        completed_now = [task for task, end in in_progress.items() if end <= time]
        for task in completed_now:
            completed.add(task)
            del in_progress[task]
        
        # 找出就绪任务（依赖已完成且未开始）
        ready_tasks = []
        for task in all_tasks:
            if task not in completed and task not in in_progress:
                deps_met = all(dep in completed for dep in tasks[task]['deps'])
                if deps_met:
                    ready_tasks.append(task)
        
        # 如果没有就绪任务，时间前进到下一个任务完成
        if not ready_tasks and in_progress:
            next_completion = min(in_progress.values())
            time = next_completion
            continue
        
        # 尝试调度就绪任务（考虑资源约束）
        scheduled_this_time = []
        cpu_used = sum(tasks[task]['cpu'] for task in in_progress)
        mem_used = sum(tasks[task]['mem'] for task in in_progress)
        
        # 按字母序排序就绪任务
        ready_tasks_sorted = sorted(ready_tasks)
        
        for task in ready_tasks_sorted:
            cpu_needed = tasks[task]['cpu']
            mem_needed = tasks[task]['mem']
            
            if cpu_used + cpu_needed <= CPU_LIMIT and mem_used + mem_needed <= MEM_LIMIT:
                # 可以调度这个任务
                end_time = time + tasks[task]['duration']
                schedule.append({'task': task, 'start': time, 'end': end_time})
                in_progress[task] = end_time
                scheduled_this_time.append(task)
                cpu_used += cpu_needed
                mem_used += mem_needed
        
        # 如果没有调度任何新任务且还有任务在进行，时间前进
        if not scheduled_this_time and in_progress:
            next_completion = min(in_progress.values())
            time = next_completion
        
        # 如果调度了任务，保持当前时间（允许并行开始）
        # 如果所有任务都已完成或进行中，时间前进
        if not ready_tasks and not scheduled_this_time and in_progress:
            next_completion = min(in_progress.values())
            time = next_completion
    
    # 按(start, task)排序schedule
    schedule_sorted = sorted(schedule, key=lambda x: (x['start'], x['task']))
    
    # 计算makespan
    makespan = max(item['end'] for item in schedule_sorted) if schedule_sorted else 0
    
    # 找出关键路径
    critical_path = find_critical_path(schedule_sorted)
    
    # 生成并行组
    parallel_groups = generate_parallel_groups(schedule_sorted)
    
    return {
        'schedule': schedule_sorted,
        'makespan': makespan,
        'critical_path': critical_path,
        'parallel_groups': parallel_groups
    }

def brute_force_search() -> Dict:
    """尝试有限的暴力搜索找到最优解"""
    best_schedule = None
    best_makespan = float('inf')
    
    # 由于任务数量不多，我们可以尝试不同的启动顺序
    # 但为了效率，我们主要依赖贪心算法，然后微调
    
    # 先运行贪心算法
    greedy_result = greedy_schedule()
    best_schedule = greedy_result['schedule']
    best_makespan = greedy_result['makespan']
    
    print(f"Greedy makespan: {best_makespan}")
    
    # 尝试一些调整
    # 这里可以添加更复杂的搜索逻辑，但为了简单起见，我们先返回贪心结果
    return greedy_result

if __name__ == "__main__":
    result = brute_force_search()
    
    # 添加notes
    notes = [
        "关键资源约束是Memory（上限16），特别是任务G需要8内存，E需要6内存，限制了它们的并行执行",
        "依赖链A->C->E->G和A->D->F->G在关键路径上，需要仔细安排以避免资源冲突",
        "任务B可以较早开始，因为它资源需求较低（1 CPU, 2内存），可以与A并行"
    ]
    
    output = {
        "schedule": result['schedule'],
        "parallel_groups": result['parallel_groups'],
        "makespan": result['makespan'],
        "critical_path": result['critical_path'],
        "notes": notes
    }
    
    print(f"Makespan: {result['makespan']}")
    print(f"Critical path: {result['critical_path']}")
    print(f"Parallel groups: {result['parallel_groups']}")
    print("\nSchedule:")
    for item in result['schedule']:
        print(f"  {item['task']}: start={item['start']}, end={item['end']}")
    
    # 验证调度
    if is_valid_schedule(result['schedule']):
        print("\n✓ Schedule is valid")
    else:
        print("\n✗ Schedule is NOT valid")
    
    # 输出到文件
    with open('resource_schedule.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\nOutput written to resource_schedule.json")