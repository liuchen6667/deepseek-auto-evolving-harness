import json

with open('task_catalog.json') as f:
    tasks = json.load(f)['tasks']

print('任务资源需求：')
for task in tasks:
    print(f"{task['task_id']}: priority {task['priority']}, {task['duration_windows']}窗口, {task['cpu']} cpu, {task['ram_gb']} ram_gb, deadline {task['deadline_minute']}分钟, 依赖 {task['depends_on']}")
