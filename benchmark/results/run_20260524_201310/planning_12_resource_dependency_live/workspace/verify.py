#!/usr/bin/env python3
import json

# 从文件读取调度
with open('resource_schedule.json', 'r') as f:
    data = json.load(f)

schedule = {item['task']: item for item in data['schedule']}

# 任务依赖
deps = {
    'A': [],
    'B': [],
    'C': ['A'],
    'D': ['A'],
    'E': ['B', 'C'],
    'F': ['D'],
    'G': ['E', 'F'],
    'H': ['E'],
    'I': ['G', 'H']
}

print("依赖检查:")
all_ok = True
for task, dep_list in deps.items():
    task_start = schedule[task]['start']
    for dep in dep_list:
        dep_end = schedule[dep]['end']
        if dep_end > task_start:
            print(f"错误: {task} 开始于 {task_start}, 但依赖 {dep} 结束于 {dep_end}")
            all_ok = False
        else:
            print(f"正确: {task} 开始于 {task_start}, 依赖 {dep} 结束于 {dep_end}")

print(f"\n所有依赖满足: {all_ok}")

# 资源检查
print("\n资源使用检查:")
tasks = {
    'A': {'cpu': 2, 'mem': 4},
    'B': {'cpu': 1, 'mem': 2},
    'C': {'cpu': 3, 'mem': 4},
    'D': {'cpu': 2, 'mem': 3},
    'E': {'cpu': 4, 'mem': 6},
    'F': {'cpu': 3, 'mem': 4},
    'G': {'cpu': 5, 'mem': 8},
    'H': {'cpu': 1, 'mem': 2},
    'I': {'cpu': 2, 'mem': 2}
}

cpu_limit = 8
mem_limit = 16
makespan = data['makespan']

resource_ok = True
for t in range(makespan + 1):
    cpu_used = 0
    mem_used = 0
    running = []
    
    for task, info in schedule.items():
        if info['start'] <= t < info['end']:
            cpu_used += tasks[task]['cpu']
            mem_used += tasks[task]['mem']
            running.append(task)
    
    if cpu_used > cpu_limit or mem_used > mem_limit:
        print(f"时间 {t}: 运行 {running}, CPU={cpu_used}/{cpu_limit}, Mem={mem_used}/{mem_limit} - 超限!")
        resource_ok = False
    elif running:
        print(f"时间 {t}: 运行 {running}, CPU={cpu_used}/{cpu_limit}, Mem={mem_used}/{mem_limit}")

print(f"\n资源约束满足: {resource_ok}")

# 检查parallel_groups
print("\nparallel_groups检查:")
groups = data['parallel_groups']
for group in groups:
    if len(group) > 1:
        start_times = [schedule[task]['start'] for task in group]
        if len(set(start_times)) != 1:
            print(f"错误: 组 {group} 开始时间不一致: {start_times}")
        else:
            print(f"正确: 组 {group} 都在时间 {start_times[0]} 开始")

# 检查critical_path长度
print(f"\n关键路径长度检查:")
critical_path = data['critical_path']
total_duration = 0
for task in critical_path:
    total_duration += schedule[task]['end'] - schedule[task]['start']
print(f"关键路径 {critical_path} 总时长: {total_duration}")
print(f"Makespan: {makespan}")