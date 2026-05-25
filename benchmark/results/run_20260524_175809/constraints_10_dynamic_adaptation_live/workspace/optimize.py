#!/usr/bin/env python3

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

def feasible_in_slot(workload, slot):
    """检查工作负载在槽中是否满足latency和error约束"""
    return (workload['latency'] <= slot['latency_max'] and 
            workload['error'] <= slot['error_max'])

# 对于每个槽，找出可行的工作负载
for slot in slots:
    print(f"\n槽 {slot['start']} 可行的工作负载:")
    feasible = []
    for w in workloads:
        if feasible_in_slot(w, slot):
            feasible.append(w)
            print(f"  {w['name']}: throughput={w['throughput']}, memory={w['memory']}, concurrency={w['concurrency']}")
    
    # 尝试找到最优组合
    print(f"  内存限制: {slot['memory_max']} GB, 并发限制: {slot['concurrency_max']}")
    
    # 生成所有可能的组合
    from itertools import combinations
    best_throughput = 0
    best_combination = []
    
    for r in range(1, len(feasible) + 1):
        for combo in combinations(feasible, r):
            total_memory = sum(w['memory'] for w in combo)
            total_concurrency = sum(w['concurrency'] for w in combo)
            total_throughput = sum(w['throughput'] for w in combo)
            
            if total_memory <= slot['memory_max'] and total_concurrency <= slot['concurrency_max']:
                if total_throughput > best_throughput:
                    best_throughput = total_throughput
                    best_combination = combo
    
    if best_combination:
        names = sorted([w['name'] for w in best_combination])
        print(f"  最优组合: {names}, throughput={best_throughput}")
        print(f"  使用内存: {sum(w['memory'] for w in best_combination):.1f} GB")
        print(f"  使用并发: {sum(w['concurrency'] for w in best_combination)}")
    else:
        print("  没有可行组合")

# 现在考虑动态适应：工作负载可以延迟或取消
print("\n=== 动态适应策略 ===")
print("注意：某些工作负载可以延迟（delayable=true）或取消（cancelable=true）")
print("realtime_search: 不可延迟，不可取消")
print("billing_sync: 可延迟，不可取消")
print("image_backfill: 可延迟，可取消")
print("report_export: 可延迟，可取消")
print("fraud_guard: 不可延迟，不可取消")

print("\n策略思考：")
print("1. 槽0-10：可以运行realtime_search、billing_sync和fraud_guard")
print("2. 槽15：只能运行realtime_search和fraud_guard")
print("3. 槽20：只能运行fraud_guard")
print("4. image_backfill和report_export在所有槽中都不可行")
print("5. billing_sync在槽15和20不可行，但可以延迟到更早的槽")
