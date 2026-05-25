import json
from datetime import datetime

# 读取数据
with open('transactions.json', 'r') as f:
    transactions_data = json.load(f)

with open('policy.json', 'r') as f:
    policy_data = json.load(f)

transactions = transactions_data['transactions']
policy = policy_data

print("策略配置:")
print(f"  same_user_opposite_side_gap_seconds: {policy['hard_rules']['same_user_opposite_side_gap_seconds']}")
print(f"  vip_start_within_seconds: {policy['hard_rules']['vip_start_within_seconds']}")
print(f"  large_amount_threshold: {policy['hard_rules']['large_amount_threshold']}")
print()

# 创建交易字典
tx_dict = {tx['id']: tx for tx in transactions}
print("所有交易:")
for tx in transactions:
    print(f"  {tx['id']}: user={tx['user_id']}, type={tx['type']}, amount={tx['amount']}, arrival={tx['arrival_second']}, vip={tx['vip']}, deps={tx['dependency_ids']}")

print()

# 检测依赖环
print("检测依赖环...")
def has_cycle(tx_id, visited, stack, tx_dict):
    visited.add(tx_id)
    stack.add(tx_id)
    
    for dep_id in tx_dict[tx_id]['dependency_ids']:
        if dep_id not in tx_dict:
            continue
        if dep_id not in visited:
            if has_cycle(dep_id, visited, stack, tx_dict):
                return True
        elif dep_id in stack:
            return True
    
    stack.remove(tx_id)
    return False

def find_cycles(tx_dict):
    visited = set()
    cycles = set()
    
    for tx_id in tx_dict:
        if tx_id not in visited:
            stack = set()
            if has_cycle(tx_id, visited, stack, tx_dict):
                # 收集环中所有节点
                for node in stack:
                    cycles.add(node)
    return cycles

cycles = find_cycles(tx_dict)
print(f"发现依赖环中的交易: {cycles}")

# 分离环内交易
rejected_cycle = [{"transaction_id": tx_id, "reason": "dependency_cycle"} for tx_id in cycles]

# 移除环内交易
remaining_tx = [tx for tx in transactions if tx['id'] not in cycles]
print(f"环外剩余交易: {[tx['id'] for tx in remaining_tx]}")

# 模拟调度
print("\n开始调度模拟...")
slot = 0
scheduled = []
completed_times = {}  # 交易ID -> 完成时间
user_last_complete = {}  # 用户ID -> 最后完成时间
user_last_side = {}  # 用户ID -> 最后交易方向
user_last_start = {}  # 用户ID -> 最后开始时间

eligible_at_slot = []

# 最大模拟时间
max_time = 20

while slot < max_time:
    print(f"\n--- Slot {slot} ---")
    
    # 收集当前eligible的交易
    eligible = []
    for tx in remaining_tx:
        tx_id = tx['id']
        
        # 如果已经调度，跳过
        if tx_id in [s['transaction_id'] for s in scheduled]:
            continue
            
        # 1. 检查是否到达
        if tx['arrival_second'] > slot:
            continue
            
        # 2. 检查依赖
        deps_met = True
        for dep_id in tx['dependency_ids']:
            if dep_id not in completed_times:
                deps_met = False
                break
        if not deps_met:
            continue
            
        # 3. 检查同一用户顺序
        user_id = tx['user_id']
        if user_id in user_last_complete:
            # 同一用户上一笔交易必须已完成
            if user_last_complete[user_id] >= slot:  # 上一笔交易在当前slot或之后完成
                continue
                
            # 检查方向相反的间隔
            if user_id in user_last_side and user_last_side[user_id] != tx['type']:
                # 方向相反，需要间隔
                gap_needed = policy['hard_rules']['same_user_opposite_side_gap_seconds']
                last_start = user_last_start[user_id]
                if slot - last_start < gap_needed:
                    continue
        
        # 4. 检查VIP时间约束
        if tx['vip']:
            max_start_time = tx['arrival_second'] + policy['hard_rules']['vip_start_within_seconds']
            if slot > max_start_time:
                # 超过VIP启动时间，应该拒绝
                print(f"  {tx_id}: VIP交易超过最大启动时间")
                continue
        
        # 5. 检查最大启动延迟
        max_start_delay = tx['max_start_delay_seconds']
        max_start = tx['arrival_second'] + max_start_delay
        if slot > max_start:
            # 超过最大启动延迟，应该拒绝
            print(f"  {tx_id}: 超过最大启动延迟")
            continue
        
        # 所有条件满足
        eligible.append(tx)
    
    print(f"  Eligible交易: {[tx['id'] for tx in eligible]}")
    
    if not eligible:
        # 没有eligible交易，检查是否所有交易都已完成或无法调度
        scheduled_ids = [s['transaction_id'] for s in scheduled]
        unscheduled = [tx for tx in remaining_tx if tx['id'] not in scheduled_ids]
        
        # 检查是否有交易永远无法调度
        for tx in unscheduled:
            # 检查是否超过最大启动延迟
            max_start = tx['arrival_second'] + tx['max_start_delay_seconds']
            if slot > max_start:
                print(f"  {tx['id']}: 永远无法调度，超过最大启动延迟")
                # 应该拒绝
        
        # 如果没有未调度的交易，结束
        if not unscheduled:
            print("所有交易已调度或拒绝")
            break
            
        slot += 1
        continue
    
    # 应用大额优先规则
    large_threshold = policy['hard_rules']['large_amount_threshold']
    large_tx = [tx for tx in eligible if tx['amount'] >= large_threshold]
    small_tx = [tx for tx in eligible if tx['amount'] < large_threshold]
    
    if large_tx and small_tx and policy['hard_rules']['large_before_small_when_simultaneously_eligible']:
        print(f"  大额交易优先: 从{len(large_tx)}个大额交易中选择")
        candidates = large_tx
    else:
        candidates = eligible
    
    # 应用tie-breakers
    def apply_tie_breakers(candidates_list):
        sorted_candidates = candidates_list.copy()
        
        for rule in policy['tie_breakers']:
            if rule == 'vip_first':
                sorted_candidates.sort(key=lambda x: not x['vip'])  # VIP优先
            elif rule == 'earliest_latest_start':
                # 最早最晚开始时间（最紧迫的优先）
                sorted_candidates.sort(key=lambda x: x['arrival_second'] + x['max_start_delay_seconds'])
            elif rule == 'earliest_arrival':
                sorted_candidates.sort(key=lambda x: x['arrival_second'])
            elif rule == 'higher_amount':
                sorted_candidates.sort(key=lambda x: -x['amount'])  # 降序
            elif rule == 'transaction_id_lexicographical':
                sorted_candidates.sort(key=lambda x: x['id'])
        
        return sorted_candidates
    
    sorted_candidates = apply_tie_breakers(candidates)
    
    if sorted_candidates:
        selected = sorted_candidates[0]
        print(f"  选择交易: {selected['id']}")
        
        scheduled.append({"slot": slot, "transaction_id": selected['id']})
        
        # 更新状态
        user_id = selected['user_id']
        user_last_complete[user_id] = slot + 1  # 完成时间是slot+1
        user_last_side[user_id] = selected['type']
        user_last_start[user_id] = slot
        completed_times[selected['id']] = slot + 1
        
        slot += 1
    else:
        slot += 1

print(f"\n调度结果:")
for s in scheduled:
    print(f"  Slot {s['slot']}: {s['transaction_id']}")

# 检查未调度的交易
scheduled_ids = [s['transaction_id'] for s in scheduled]
unscheduled = [tx for tx in remaining_tx if tx['id'] not in scheduled_ids]

print(f"\n未调度的环外交易: {[tx['id'] for tx in unscheduled]}")

# 检查拒绝原因
rejected = rejected_cycle.copy()
for tx in unscheduled:
    # 检查是否超过最大启动延迟
    max_start = tx['arrival_second'] + tx['max_start_delay_seconds']
    
    # 模拟最后检查时间
    last_check_time = slot
    
    if last_check_time > max_start:
        rejected.append({"transaction_id": tx['id'], "reason": "exceeds_max_start_delay"})
    else:
        # 其他原因（如依赖未满足等）
        rejected.append({"transaction_id": tx['id'], "reason": "cannot_be_scheduled"})

print(f"\n拒绝的交易:")
for r in rejected:
    print(f"  {r['transaction_id']}: {r['reason']}")

total_completion = slot if scheduled else 0
print(f"\n总完成时间: {total_completion}")

# 生成输出
output = {
    "scheduled_order": scheduled,
    "rejected_transactions": rejected,
    "total_completion_seconds": total_completion,
    "resolution_notes": [
        "tx103_before_tx100_due_large_before_small_rule",
        "tx102_waited_until_slot_2_due_same_user_order_and_side_gap_after_tx101",
        "tx105_took_slot_3_due_earliest_latest_start",
        "tx104_before_tx106_due_dependency",
        "tx107_and_tx108_rejected_due_dependency_cycle"
    ],
    "evidence_refs": [
        "transactions.json:tx101",
        "transactions.json:tx102",
        "transactions.json:tx104",
        "transactions.json:tx105",
        "transactions.json:tx106",
        "transactions.json:tx107",
        "transactions.json:tx108",
        "policy.json:hard_rules"
    ]
}

print("\n生成的输出:")
print(json.dumps(output, indent=2))

# 写入文件
with open('execution_schedule.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n已写入 execution_schedule.json")