#!/usr/bin/env python3

# 分析工作负载和槽约束
workloads = [
    {'name': 'realtime_search', 'throughput': 12, 'latency': 2.6, 'memory': 0.7, 'concurrency': 6, 'error': 0.4, 'delayable': False, 'cancelable': False},
    {'name': 'billing_sync', 'throughput': 7, 'latency': 4.4, 'memory': 0.9, 'concurrency': 3, 'error': 0.6, 'delayable': True, 'cancelable': False},
    {'name': 'image_backfill', 'throughput': 9, 'latency': 6.0, 'memory': 0.8, 'concurrency': 5, 'error': 0.2, 'delayable': True, 'cancelable': True},
    {'name': 'report_export', 'throughput': 4, 'latency': 3.2, 'memory': 0.6, 'concurrency': 2, 'error': 1.5, 'delayable': True, 'cancelable': True},
    {'name': 'fraud_guard', 'throughput': 6, 'latency': 2.1, 'memory': 0.5, 'concurrency': 4, 'error': 0.08, 'delayable': False, 'cancelable': False}
]

slots = [
    {'start': 0, 'latency_max': 5, 'memory_max': 2.0, 'concurrency_max': 10, 'error_max': 1.0},
    {'start': 5, 'latency_max': 5, 'memory_max': 1.0, 'concurrency_max': 10, 'error_max': 1.0},
    {'start': 10, 'latency_max': 5, 'memory_max': 1.0, 'concurrency_max': 20, 'error_max': 1.0},
    {'start': 15, 'latency_max': 3, 'memory_max': 1.0, 'concurrency_max': 20, 'error_max': 1.0},
    {'start': 20, 'latency_max': 3, 'memory_max': 1.0, 'concurrency_max': 20, 'error_max': 0.1}
]

print('工作负载分析：')
for w in workloads:
    print(f"{w['name']}: throughput={w['throughput']}, latency={w['latency']}, memory={w['memory']}, concurrency={w['concurrency']}, error={w['error']}")

print('\n槽约束分析：')
for s in slots:
    print(f"槽 {s['start']}: latency_max={s['latency_max']}, memory_max={s['memory_max']}, concurrency_max={s['concurrency_max']}, error_max={s['error_max']}")

print('\n每个工作负载在每个槽中的可行性（仅考虑latency和error）：')
for s in slots:
    print(f"\n槽 {s['start']} (latency_max={s['latency_max']}, error_max={s['error_max']}):")
    for w in workloads:
        latency_ok = w['latency'] <= s['latency_max']
        error_ok = w['error'] <= s['error_max']
        if latency_ok and error_ok:
            print(f"  {w['name']}: OK (latency {w['latency']} ≤ {s['latency_max']}, error {w['error']} ≤ {s['error_max']})")
        else:
            issues = []
            if not latency_ok:
                issues.append(f"latency {w['latency']} > {s['latency_max']}")
            if not error_ok:
                issues.append(f"error {w['error']} > {s['error_max']}")
            print(f"  {w['name']}: NO ({', '.join(issues)})")

# 找出哪些工作负载在哪些槽中不可行
print('\n=== 关键约束分析 ===')
print('1. image_backfill (latency=6.0) 在槽15和槽20中不可行，因为latency_max=3')
print('2. report_export (error=1.5) 在槽20中不可行，因为error_max=0.1')
print('3. 其他工作负载在所有槽中都满足latency和error约束')

# 检查memory和concurrency约束
print('\n=== Memory和Concurrency分析 ===')
print('memory_gb总和必须在每个槽的memory_max内')
print('concurrency总和必须在每个槽的concurrency_max内')

# 计算每个工作负载的throughput/memory和throughput/concurrency比率
print('\n=== 效率分析 ===')
for w in workloads:
    throughput_per_memory = w['throughput'] / w['memory']
    throughput_per_concurrency = w['throughput'] / w['concurrency']
    print(f"{w['name']}: throughput/memory={throughput_per_memory:.2f}, throughput/concurrency={throughput_per_concurrency:.2f}")
