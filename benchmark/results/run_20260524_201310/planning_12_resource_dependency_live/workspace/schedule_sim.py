#!/usr/bin/env python3

tasks = {
    'A': {'dur': 2, 'cpu': 2, 'mem': 4, 'deps': [], 'start': None, 'end': None},
    'B': {'dur': 2, 'cpu': 1, 'mem': 2, 'deps': [], 'start': None, 'end': None},
    'C': {'dur': 3, 'cpu': 3, 'mem': 4, 'deps': ['A'], 'start': None, 'end': None},
    'D': {'dur': 2, 'cpu': 2, 'mem': 3, 'deps': ['A'], 'start': None, 'end': None},
    'E': {'dur': 4, 'cpu': 4, 'mem': 6, 'deps': ['B', 'C'], 'start': None, 'end': None},
    'F': {'dur': 3, 'cpu': 3, 'mem': 4, 'deps': ['D'], 'start': None, 'end': None},
    'G': {'dur': 5, 'cpu': 5, 'mem': 8, 'deps': ['E', 'F'], 'start': None, 'end': None},
    'H': {'dur': 1, 'cpu': 1, 'mem': 2, 'deps': ['E'], 'start': None, 'end': None},
    'I': {'dur': 2, 'cpu': 2, 'mem': 2, 'deps': ['G', 'H'], 'start': None, 'end': None}
}

cpu_limit = 8
mem_limit = 16

def is_ready(task, time, schedule):
    """检查任务是否就绪（依赖已完成）"""
    for dep in tasks[task]['deps']:
        if schedule[dep]['end'] is None or schedule[dep]['end'] > time:
            return False
    return True

def get_available_resources(time, schedule):
    """获取当前时间可用的资源"""
    cpu_used = 0
    mem_used = 0
    
    for task, info in schedule.items():
        if info['start'] is not None and info['start'] <= time < info['end']:
            cpu_used += tasks[task]['cpu']
            mem_used += tasks[task]['mem']
    
    return cpu_limit - cpu_used, mem_limit - mem_used

def greedy_schedule():
    schedule = {task: {'start': None, 'end': None} for task in tasks}
    completed = set()
    time = 0
    
    while len(completed) < len(tasks):
        # 找出就绪且未开始的任务
        ready_tasks = []
        for task in tasks:
            if task not in completed and schedule[task]['start'] is None:
                if is_ready(task, time, schedule):
                    ready_tasks.append(task)
        
        # 按字母序排序（规则：字母序更小且已就绪的任务更早启动）
        ready_tasks.sort()
        
        # 尝试启动任务
        cpu_avail, mem_avail = get_available_resources(time, schedule)
        
        for task in ready_tasks:
            if tasks[task]['cpu'] <= cpu_avail and tasks[task]['mem'] <= mem_avail:
                schedule[task]['start'] = time
                schedule[task]['end'] = time + tasks[task]['dur']
                cpu_avail -= tasks[task]['cpu']
                mem_avail -= tasks[task]['mem']
                print(f"时间 {time}: 启动 {task} (cpu={tasks[task]['cpu']}, mem={tasks[task]['mem']})")
        
        # 前进到下一个事件时间
        next_event = float('inf')
        for task in tasks:
            if schedule[task]['end'] is not None and schedule[task]['end'] > time:
                next_event = min(next_event, schedule[task]['end'])
        
        # 标记已完成的任务
        for task in tasks:
            if schedule[task]['end'] is not None and schedule[task]['end'] <= time and task not in completed:
                completed.add(task)
                print(f"时间 {time}: {task} 完成")
        
        if next_event == float('inf'):
            break
        
        time = next_event
    
    # 确保所有任务都标记为完成
    for task in tasks:
        if task not in completed:
            completed.add(task)
    
    return schedule, time

print("贪婪调度结果:")
schedule, makespan = greedy_schedule()
print(f"\n最终调度:")
for task in sorted(schedule.keys(), key=lambda x: (schedule[x]['start'] or 0, x)):
    start = schedule[task]['start']
    end = schedule[task]['end']
    if start is not None:
        print(f"{task}: {start}-{end}")

print(f"\nMakespan: {makespan}")

# 检查资源约束
print("\n资源使用检查:")
for t in range(makespan + 1):
    cpu_used = 0
    mem_used = 0
    running = []
    
    for task in tasks:
        start = schedule[task]['start']
        end = schedule[task]['end']
        if start is not None and start <= t < end:
            cpu_used += tasks[task]['cpu']
            mem_used += tasks[task]['mem']
            running.append(task)
    
    if running:
        print(f"时间 {t}: 运行 {running}, CPU={cpu_used}/{cpu_limit}, Mem={mem_used}/{mem_limit}")
        if cpu_used > cpu_limit or mem_used > mem_limit:
            print(f"  错误: 资源超限!")