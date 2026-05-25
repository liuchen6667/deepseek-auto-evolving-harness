#!/usr/bin/env python3
"""
创建最终的resource_schedule.json
"""

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

# 最优调度方案（总工期16）
schedule_times = {
    'A': {'start': 0, 'end': 2},
    'B': {'start': 0, 'end': 2},
    'C': {'start': 2, 'end': 5},
    'D': {'start': 2, 'end': 4},
    'E': {'start': 5, 'end': 9},
    'F': {'start': 4, 'end': 7},
    'G': {'start': 9, 'end': 14},
    'H': {'start': 9, 'end': 10},
    'I': {'start': 14, 'end': 16}
}

# 按(start, task)排序
sorted_schedule = sorted(
    [{'task': task, 'start': times['start'], 'end': times['end']} 
     for task, times in schedule_times.items()],
    key=lambda x: (x['start'], x['task'])
)

# 找出并行组（相同开始时间的任务）
parallel_groups = []
start_time_to_tasks = {}

for item in sorted_schedule:
    start = item['start']
    task = item['task']
    if start not in start_time_to_tasks:
        start_time_to_tasks[start] = []
    start_time_to_tasks[start].append(task)

# 创建并行组（按开始时间排序，每组内按字母序排序）
for start in sorted(start_time_to_tasks.keys()):
    tasks_at_time = sorted(start_time_to_tasks[start])
    if len(tasks_at_time) > 1:
        parallel_groups.append(tasks_at_time)

# 关键路径（基于无资源约束分析）
critical_path = ['A', 'C', 'E', 'G', 'I']

# makespan
makespan = max(item['end'] for item in sorted_schedule)

# notes
notes = [
    "关键路径 A->C->E->G->I 决定了最小工期为16，资源约束下该路径任务无法提前",
    "资源使用峰值出现在时间5-7：E(CPU4/Mem6)和F(CPU3/Mem4)并行，总CPU7/Mem10，未超限"
]

# 创建最终JSON
import json

result = {
    "schedule": sorted_schedule,
    "parallel_groups": parallel_groups,
    "makespan": makespan,
    "critical_path": critical_path,
    "notes": notes
}

# 写入文件
with open('resource_schedule.json', 'w') as f:
    json.dump(result, f, indent=2)

print("=== 最终调度方案 ===")
print(f"总工期 (makespan): {makespan}")
print(f"关键路径: {' -> '.join(critical_path)}")
print("\n调度顺序:")
for item in sorted_schedule:
    print(f"  任务 {item['task']}: 开始={item['start']}, 结束={item['end']}")

print("\n并行组:")
for group in parallel_groups:
    print(f"  {group} (同时开始于时间 {schedule_times[group[0]]['start']})")

print("\n备注:")
for note in notes:
    print(f"  - {note}")

print(f"\n已写入 resource_schedule.json")