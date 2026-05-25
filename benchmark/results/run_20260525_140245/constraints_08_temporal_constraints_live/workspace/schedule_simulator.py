import json
from datetime import datetime

# 读取输入文件
with open('transactions.json', 'r') as f:
    transactions_data = json.load(f)

with open('policy.json', 'r') as f:
    policy_data = json.load(f)

transactions = {tx['id']: tx for tx in transactions_data['transactions']}
hard_rules = policy_data['hard_rules']
tie_breakers = policy_data['tie_breakers']

print("=== 交易信息 ===")
for tx_id, tx in transactions.items():
    print(f"{tx_id}: user={tx['user_id']}, type={tx['type']}, amount={tx['amount']}, "
          f"arrival={tx['arrival_second']}, vip={tx['vip']}, "
          f"deps={tx['dependency_ids']}, max_start_delay={tx['max_start_delay_seconds']}")

print(f"\n=== 硬约束 ===")
for key, value in hard_rules.items():
    print(f"{key}: {value}")

print(f"\n=== 平局打破规则 ===")
print(tie_breakers)

# 检查依赖环
def find_dependency_cycles():
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(tx_id, path):
        if tx_id in rec_stack:
            cycle_start = path.index(tx_id)
            cycles.append(path[cycle_start:])
            return
        if tx_id in visited:
            return
            
        visited.add(tx_id)
        rec_stack.add(tx_id)
        
        for dep_id in transactions[tx_id]['dependency_ids']:
            if dep_id in transactions:
                dfs(dep_id, path + [dep_id])
        
        rec_stack.remove(tx_id)
    
    for tx_id in transactions:
        if tx_id not in visited:
            dfs(tx_id, [tx_id])
    
    # 去重和展平循环
    unique_cycles = []
    seen = set()
    for cycle in cycles:
        # 排序并转换为元组以去重
        sorted_cycle = sorted(cycle)
        cycle_tuple = tuple(sorted_cycle)
        if cycle_tuple not in seen:
            seen.add(cycle_tuple)
            unique_cycles.append(cycle)
    
    return unique_cycles

cycles = find_dependency_cycles()
print(f"\n=== 依赖环检测 ===")
if cycles:
    for cycle in cycles:
        print(f"依赖环: {cycle}")
else:
    print("无依赖环")

# 识别被拒绝的交易（依赖环）
rejected = []
if hard_rules['reject_dependency_cycles'] and cycles:
    for cycle in cycles:
        for tx_id in cycle:
            if tx_id not in [r['transaction_id'] for r in rejected]:
                rejected.append({"transaction_id": tx_id, "reason": "dependency_cycle"})

print(f"\n=== 被拒绝的交易（依赖环）===")
for r in rejected:
    print(f"{r['transaction_id']}: {r['reason']}")

# 剩余交易
remaining_tx = [tx for tx in transactions_data['transactions'] 
                if tx['id'] not in [r['transaction_id'] for r in rejected]]
print(f"\n=== 剩余交易数量: {len(remaining_tx)} ===")

# 模拟调度
scheduled = []  # 列表 of (slot, tx_id)
completed_tx = set()
user_last_tx = {}  # user_id -> (tx_id, slot, type)
user_last_slot = {}  # user_id -> 最后交易完成的slot
slot = 0

# 计算每个交易的最晚启动时间
for tx in remaining_tx:
    tx['latest_start'] = tx['arrival_second'] + tx['max_start_delay_seconds']

print("\n=== 模拟调度过程 ===")

while len(completed_tx) < len(remaining_tx):
    print(f"\n--- Slot {slot} ---")
    
    # 找出eligible的交易
    eligible = []
    for tx in remaining_tx:
        tx_id = tx['id']
        
        # 检查是否已调度
        if tx_id in completed_tx:
            continue
            
        # 1. 已经到达
        if tx['arrival_second'] > slot:
            print(f"  {tx_id}: 未到达 (arrival={tx['arrival_second']})")
            continue
            
        # 2. 依赖交易已完成
        deps_ok = True
        for dep_id in tx['dependency_ids']:
            if dep_id not in completed_tx:
                print(f"  {tx_id}: 依赖 {dep_id} 未完成")
                deps_ok = False
                break
        if not deps_ok:
            continue
            
        # 3. 同一用户的上一笔交易已经完成
        user_id = tx['user_id']
        if user_id in user_last_tx:
            last_tx_id, last_slot, last_type = user_last_tx[user_id]
            if last_tx_id not in completed_tx:
                print(f"  {tx_id}: 同一用户上一笔交易 {last_tx_id} 未完成")
                continue
        
        # 4. 如果同一用户上一笔交易与当前交易方向相反，则两者开始时间至少间隔 same_user_opposite_side_gap_seconds
        gap_ok = True
        if user_id in user_last_tx:
            last_tx_id, last_slot, last_type = user_last_tx[user_id]
            if last_type != tx['type']:  # 方向相反
                required_gap = hard_rules['same_user_opposite_side_gap_seconds']
                if slot - last_slot < required_gap:
                    print(f"  {tx_id}: 与上一笔相反方向交易 {last_tx_id} 间隔不足 "
                          f"(slot={slot}, last_slot={last_slot}, required_gap={required_gap})")
                    gap_ok = False
        if not gap_ok:
            continue
            
        # 5. VIP检查（不在此处判断是否超时，只判断是否eligible）
        # VIP超时检查将在调度时进行
        
        eligible.append(tx)
    
    print(f"  Eligible交易: {[tx['id'] for tx in eligible]}")
    
    if not eligible:
        # 没有eligible交易，时间前进
        slot += 1
        continue
    
    # 应用平局打破规则
    # 首先检查VIP超时
    vip_timeout = hard_rules['vip_start_within_seconds']
    vip_eligible = [tx for tx in eligible if tx['vip']]
    vip_timeout_candidates = []
    
    for tx in vip_eligible:
        latest_vip_start = tx['arrival_second'] + vip_timeout
        if slot > latest_vip_start:
            print(f"  VIP交易 {tx['id']} 已超时 (arrival={tx['arrival_second']}, "
                  f"latest_vip_start={latest_vip_start}, current_slot={slot})")
        else:
            vip_timeout_candidates.append(tx)
    
    # 如果有未超时的VIP交易，优先考虑它们
    candidates = vip_timeout_candidates if vip_timeout_candidates else eligible
    
    # 应用大额优先规则
    large_threshold = hard_rules['large_amount_threshold']
    if hard_rules['large_before_small_when_simultaneously_eligible']:
        large_candidates = [tx for tx in candidates if tx['amount'] >= large_threshold]
        small_candidates = [tx for tx in candidates if tx['amount'] < large_threshold]
        
        if large_candidates:
            print(f"  大额交易: {[tx['id'] for tx in large_candidates]}")
            candidates = large_candidates
        else:
            print(f"  小额交易: {[tx['id'] for tx in small_candidates]}")
    
    # 应用平局打破规则
    def apply_tie_breakers(candidate_list):
        if len(candidate_list) <= 1:
            return candidate_list
            
        sorted_list = candidate_list.copy()
        
        for rule in tie_breakers:
            print(f"    应用规则: {rule}")
            if rule == "vip_first":
                sorted_list.sort(key=lambda x: (not x['vip'], x['id']))
            elif rule == "earliest_latest_start":
                sorted_list.sort(key=lambda x: x['latest_start'])
            elif rule == "earliest_arrival":
                sorted_list.sort(key=lambda x: x['arrival_second'])
            elif rule == "higher_amount":
                sorted_list.sort(key=lambda x: -x['amount'])  # 降序
            elif rule == "transaction_id_lexicographical":
                sorted_list.sort(key=lambda x: x['id'])
            
            # 检查是否已完全排序
            if len(set([tx['id'] for tx in sorted_list])) == len(sorted_list):
                break
        
        return sorted_list
    
    sorted_candidates = apply_tie_breakers(candidates)
    
    if sorted_candidates:
        selected = sorted_candidates[0]
        print(f"  选择交易: {selected['id']}")
        
        # 检查VIP超时
        if selected['vip']:
            latest_vip_start = selected['arrival_second'] + vip_timeout
            if slot > latest_vip_start:
                print(f"  ERROR: VIP交易 {selected['id']} 已超时！")
        
        # 调度交易
        scheduled.append({"slot": slot, "transaction_id": selected['id']})
        completed_tx.add(selected['id'])
        
        # 更新用户最后交易信息
        user_id = selected['user_id']
        user_last_tx[user_id] = (selected['id'], slot, selected['type'])
        
        # 时间前进到下一个slot
        slot += 1
    else:
        # 没有候选交易，时间前进
        slot += 1

print(f"\n=== 调度结果 ===")
for s in scheduled:
    print(f"Slot {s['slot']}: {s['transaction_id']}")

print(f"\n=== 未调度的交易 ===")
unscheduled = [tx for tx in remaining_tx if tx['id'] not in completed_tx]
for tx in unscheduled:
    print(f"{tx['id']}")

# 检查是否有交易因为约束无法调度
for tx in unscheduled:
    # 检查是否因为VIP超时而无法调度
    if tx['vip']:
        vip_timeout = hard_rules['vip_start_within_seconds']
        latest_vip_start = tx['arrival_second'] + vip_timeout
        # 计算最晚可能的调度时间
        max_possible_slot = len(remaining_tx) - 1  # 最坏情况
        if latest_vip_start < max_possible_slot:
            print(f"  {tx['id']} 可能因为VIP超时而无法调度")
    
    # 检查是否因为依赖无法满足
    for dep_id in tx['dependency_ids']:
        if dep_id not in completed_tx and dep_id in [tx['id'] for tx in remaining_tx]:
            print(f"  {tx['id']} 依赖 {dep_id} 但依赖交易未调度")

print(f"\n总完成时间: {slot} 秒")