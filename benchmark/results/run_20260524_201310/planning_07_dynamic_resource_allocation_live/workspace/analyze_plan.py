import json
import yaml

# 读取所有文件
with open('resource_windows.json') as f:
    windows_data = json.load(f)

with open('task_catalog.json') as f:
    tasks_data = json.load(f)

with open('baseline_service.json') as f:
    baseline_data = json.load(f)

with open('scheduler_objectives.json') as f:
    objectives = json.load(f)

with open('allocation_rules.yaml') as f:
    rules = yaml.safe_load(f)

# 打印基本信息
print("=== 资源窗口 ===")
for w in windows_data['windows']:
    print(f"{w['window_id']}: {w['minutes']}, CPU: {w['cpu']}, RAM: {w['ram_gb']}")

print("\n=== 任务列表 ===")
for t in tasks_data['tasks']:
    print(f"{t['task_id']}: 优先级 {t['priority']}, {t['duration_windows']}窗口, CPU: {t['cpu']}, RAM: {t['ram_gb']}, deadline: {t['deadline_minute']}, 依赖: {t['depends_on']}")

print("\n=== Baseline服务 ===")
print(f"{baseline_data['service_id']}: CPU: {baseline_data['resource_reservation']['cpu']}, RAM: {baseline_data['resource_reservation']['ram_gb']}")

print("\n=== 调度目标 ===")
print(f"必须启动: {objectives['must_start']}")
print(f"优先级: {objectives['objective_priority']}")
print(f"最早可行启动: {objectives['earliest_feasible_start_required']}")

print("\n=== 规则 ===")
print(f"任务顺序规则: {rules['hard_rules']['task_order_rule']}")
print(f"重分配动作: {rules['reallocation_action_codes']}")
print(f"延期原因: {rules['defer_reason_codes']}")

# 计算可用资源
print("\n=== 扣除baseline后的可用资源 ===")
baseline_cpu = baseline_data['resource_reservation']['cpu']
baseline_ram = baseline_data['resource_reservation']['ram_gb']

available_resources = {}
for w in windows_data['windows']:
    window_id = w['window_id']
    available_cpu = w['cpu'] - baseline_cpu
    available_ram = w['ram_gb'] - baseline_ram
    available_resources[window_id] = {'cpu': available_cpu, 'ram_gb': available_ram}
    print(f"{window_id}: CPU: {available_cpu}, RAM: {available_ram}")