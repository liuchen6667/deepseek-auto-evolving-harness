import json
from collections import defaultdict

# 任务数据
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

CPU_LIMIT = 8
MEM_LIMIT = 16

def simulate_schedule():
    # 跟踪任务状态
    completed = set()
    in_progress = {}  # task -> {'start': x, 'end': y, 'cpu': z, 'mem': w}
    ready_tasks = []
    schedule = []
    time = 0
    
    # 初始化就绪任务（没有依赖的）
    for task, info in tasks.items():
        if not info['deps']:
            ready_tasks.append(task)
    
    # 按字母序排序（根据规则）
    ready_tasks.sort()
    
    while len(completed) < len(tasks):
        # 检查是否有任务完成
        completed_at_time = []
        for task, data in list(in_progress.items()):
            if data['end'] == time:
                completed_at_time.append(task)
        
        for task in completed_at_time:
            completed.add(task)
            del in_progress[task]
            schedule.append({'task': task, 'start': time - tasks[task]['duration'], 'end': time})
        
        # 更新就绪任务列表
        ready_tasks = []
        for task, info in tasks.items():
            if task not in completed and task not in in_progress:
                # 检查依赖是否都完成
                deps_met = all(dep in completed for dep in info['deps'])
                if deps_met:
                    ready_tasks.append(task)
        
        ready_tasks.sort()  # 按字母序排序
        
        # 尝试启动就绪任务
        for task in ready_tasks[:]:  # 使用副本以便修改
            cpu_used = sum(data['cpu'] for data in in_progress.values())
            mem_used = sum(data['mem'] for data in in_progress.values())
            
            cpu_needed = tasks[task]['cpu']
            mem_needed = tasks[task]['mem']
            
            if cpu_used + cpu_needed <= CPU_LIMIT and mem_used + mem_needed <= MEM_LIMIT:
                # 可以启动任务
                in_progress[task] = {
                    'start': time,
                    'end': time + tasks[task]['duration'],
                    'cpu': cpu_needed,
                    'mem': mem_needed
                }
                ready_tasks.remove(task)
        
        # 打印当前时间点的状态
        print(f"时间 {time}:")
        print(f"  进行中的任务: {list(in_progress.keys())}")
        print(f"  就绪任务: {ready_tasks}")
        print(f"  已完成: {sorted(completed)}")
        if in_progress:
            cpu_used = sum(data['cpu'] for data in in_progress.values())
            mem_used = sum(data['mem'] for data in in_progress.values())
            print(f"  资源使用: CPU={cpu_used}/{CPU_LIMIT}, Memory={mem_used}/{MEM_LIMIT}")
        print()
        
        # 如果没有任务在进行，但还有未完成的任务，直接跳到下一个任务完成时间
        if not in_progress and len(completed) < len(tasks):
            # 这不应该发生，但为了安全
            time += 1
        else:
            # 找到下一个任务完成时间
            next_completion = min(data['end'] for data in in_progress.values()) if in_progress else time + 1
            time = next_completion
    
    # 按start时间排序schedule
    schedule.sort(key=lambda x: (x['start'], x['task']))
    
    return schedule, time

if __name__ == "__main__":
    schedule, makespan = simulate_schedule()
    
    print("\n最终调度:")
    for s in schedule:
        print(f"  {s['task']}: start={s['start']}, end={s['end']}")
    
    print(f"\nMakespan: {makespan}")