import json
import itertools

# 加载数据
with open('workloads.json') as f:
    workloads_data = json.load(f)
    workloads = workloads_data['workloads']

with open('slot_constraints.json') as f:
    slots_data = json.load(f)
    slots = slots_data['slots']

# 创建工作负载字典
workload_dict = {w['workload']: w for w in workloads}

# 为每个槽找到最佳组合
def find_best_for_slot(slot):
    slot_start = slot['slot_start']
    latency_max = slot['latency_s_max']
    memory_max = slot['memory_gb_max']
    concurrency_max = slot['concurrency_max']
    error_max = slot['error_rate_pct_max']
    
    # 筛选可行的工作负载
    feasible = []
    for w in workloads:
        if w['latency_s'] <= latency_max and w['error_rate_pct'] <= error_max:
            feasible.append(w)
    
    if not feasible:
        return [], 0
    
    # 尝试所有组合（最多3个，因为资源有限）
    best_throughput = 0
    best_combination = []
    
    for r in range(1, min(4, len(feasible) + 1)):
        for combo in itertools.combinations(feasible, r):
            total_memory = sum(w['memory_gb'] for w in combo)
            total_concurrency = sum(w['concurrency'] for w in combo)
            total_throughput = sum(w['throughput_units'] for w in combo)
            
            if total_memory <= memory_max and total_concurrency <= concurrency_max:
                if total_throughput > best_throughput:
                    best_throughput = total_throughput
                    best_combination = combo
    
    # 按字母排序
    best_names = sorted([w['workload'] for w in best_combination])
    return best_names, best_throughput

# 为每个槽计算最佳决策
slot_decisions = []
for slot in slots:
    active_workloads, throughput = find_best_for_slot(slot)
    slot_decisions.append({
        "slot_start": slot['slot_start'],
        "active_workloads": active_workloads,
        "throughput_units": throughput
    })
    print(f"Slot {slot['slot_start']}: {active_workloads} = {throughput} throughput")

# 计算总吞吐量
total_completed_units = sum(decision['throughput_units'] for decision in slot_decisions)
print(f"\nTotal completed units: {total_completed_units}")

# 确定delayed和canceled的工作负载
# 收集所有运行过的工作负载
run_workloads = set()
for decision in slot_decisions:
    run_workloads.update(decision['active_workloads'])

final_delayed = []
final_canceled = []

for w in workloads:
    if w['workload'] not in run_workloads:
        if w['delayable'] and not w['cancelable']:
            final_delayed.append(w['workload'])
        elif w['cancelable']:
            final_canceled.append(w['workload'])

print(f"\nFinal delayed workloads: {sorted(final_delayed)}")
print(f"Final canceled workloads: {sorted(final_canceled)}")

# 创建最终输出
output = {
    "slot_decisions": slot_decisions,
    "final_delayed_workloads": sorted(final_delayed),
    "final_canceled_workloads": sorted(final_canceled),
    "total_completed_units": total_completed_units,
    "notes": [
        "Slot 5的内存限制1.0GB导致只能运行单个工作负载，选择了吞吐量最高的realtime_search(12)，放弃了billing_sync(7)和fraud_guard(6)",
        "Slot 20的错误率限制0.1%非常严格，只有fraud_guard满足要求，因为其错误率0.08%≤0.1%，而realtime_search的0.4%>0.1%",
        "image_backfill在所有槽中因延迟6.0s>5s而不可行，report_export因错误率1.5%>1.0%在大多数槽中不可行，两者均可取消"
    ]
}

# 保存结果
with open('adaptation_plan.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nAdaptation plan saved to adaptation_plan.json")
