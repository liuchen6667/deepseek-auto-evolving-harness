#!/usr/bin/env python3
import json
import yaml

# 读取所有输入文件
with open('resource_windows.json') as f:
    resource_windows = json.load(f)

with open('task_catalog.json') as f:
    task_catalog = json.load(f)

with open('baseline_service.json') as f:
    baseline_service = json.load(f)

with open('scheduler_objectives.json') as f:
    scheduler_objectives = json.load(f)

with open('allocation_rules.yaml') as f:
    allocation_rules = yaml.safe_load(f)

# 提取数据
windows = resource_windows['windows']
tasks = task_catalog['tasks']
baseline_cpu = baseline_service['resource_reservation']['cpu']
baseline_ram = baseline_service['resource_reservation']['ram_gb']

# 计算每个窗口扣除基线后的可用资源
available_resources = {}
for window in windows:
    window_id = window['window_id']
    available_resources[window_id] = {
        'cpu': window['cpu'] - baseline_cpu,
        'ram_gb': window['ram_gb'] - baseline_ram,
        'minutes': window['minutes']
    }

print("可用资源（扣除基线后）:")
for w_id, res in available_resources.items():
    print(f"  {w_id}: CPU={res['cpu']}, RAM={res['ram_gb']}, minutes={res['minutes']}")

# 任务字典
task_dict = {task['task_id']: task for task in tasks}

# 优先级映射
priority_map = {'p0': 0, 'p1': 1, 'p2': 2, 'p3': 3}

# 按优先级、截止时间、task_id排序
sorted_tasks = sorted(tasks, key=lambda x: (
    priority_map[x['priority']],
    x['deadline_minute'],
    x['task_id']
))

print("\n任务排序（优先级、截止时间、task_id）:")
for task in sorted_tasks:
    print(f"  {task['task_id']}: priority={task['priority']}, deadline={task['deadline_minute']}, duration={task['duration_windows']}窗口, CPU={task['cpu']}, RAM={task['ram_gb']}")

# 依赖关系
dependencies = {}
for task in tasks:
    dependencies[task['task_id']] = task['depends_on']

print("\n依赖关系:")
for task_id, deps in dependencies.items():
    if deps:
        print(f"  {task_id} 依赖于: {deps}")