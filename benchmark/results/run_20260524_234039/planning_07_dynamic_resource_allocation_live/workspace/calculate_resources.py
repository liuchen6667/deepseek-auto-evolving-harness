import json

with open('resource_windows.json') as f:
    windows = json.load(f)['windows']

with open('baseline_service.json') as f:
    baseline = json.load(f)['resource_reservation']

print('窗口可用资源（扣除基线服务后）：')
for w in windows:
    avail_cpu = w['cpu'] - baseline['cpu']
    avail_ram = w['ram_gb'] - baseline['ram_gb']
    print(f"{w['window_id']}: {avail_cpu} cpu, {avail_ram} ram_gb")
