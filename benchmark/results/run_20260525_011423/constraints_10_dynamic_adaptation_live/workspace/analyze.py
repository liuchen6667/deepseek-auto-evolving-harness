import json

# 加载数据
with open('workloads.json') as f:
    workloads_data = json.load(f)
    workloads = workloads_data['workloads']

with open('slot_constraints.json') as f:
    slots_data = json.load(f)
    slots = slots_data['slots']

print('=== 工作负载分析 ===')
for w in workloads:
    print(f"{w['workload']}: throughput={w['throughput_units']}, latency={w['latency_s']}, memory={w['memory_gb']}, concurrency={w['concurrency']}, error={w['error_rate_pct']}, delayable={w['delayable']}, cancelable={w['cancelable']}")

print('\n=== 时间槽约束 ===')
for s in slots:
    print(f"Slot {s['slot_start']}: latency_max={s['latency_s_max']}, memory_max={s['memory_gb_max']}, concurrency_max={s['concurrency_max']}, error_max={s['error_rate_pct_max']}")

print('\n=== 每个工作负载在每个槽的可行性 ===')
for s in slots:
    print(f"\nSlot {s['slot_start']} (latency_max={s['latency_s_max']}, error_max={s['error_rate_pct_max']}):")
    for w in workloads:
        latency_ok = w['latency_s'] <= s['latency_s_max']
        error_ok = w['error_rate_pct'] <= s['error_rate_pct_max']
        if latency_ok and error_ok:
            print(f"  ✓ {w['workload']}: latency={w['latency_s']}≤{s['latency_s_max']}, error={w['error_rate_pct']}≤{s['error_rate_pct_max']}")
        else:
            issues = []
            if not latency_ok:
                issues.append(f"latency={w['latency_s']}>{s['latency_s_max']}")
            if not error_ok:
                issues.append(f"error={w['error_rate_pct']}>{s['error_rate_pct_max']}")
            print(f"  ✗ {w['workload']}: {'; '.join(issues)}")

print('\n=== 吞吐量排序 ===')
sorted_workloads = sorted(workloads, key=lambda x: x['throughput_units'], reverse=True)
for w in sorted_workloads:
    print(f"{w['workload']}: {w['throughput_units']} units")
