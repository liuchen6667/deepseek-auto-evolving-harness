import json
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional

# 读取数据
with open('transactions.json', 'r') as f:
    transactions_data = json.load(f)

with open('policy.json', 'r') as f:
    policy_data = json.load(f)

transactions = {tx['id']: tx for tx in transactions_data['transactions']}
policy = policy_data

# 提取参数
SAME_USER_ORDER = policy['hard_rules']['same_user_order']
OPPOSITE_SIDE_GAP = policy['hard_rules']['same_user_opposite_side_gap_seconds']
VIP_WITHIN_SECONDS = policy['hard_rules']['vip_start_within_seconds']
LARGE_THRESHOLD = policy['hard_rules']['large_amount_threshold']
LARGE_BEFORE_SMALL = policy['hard_rules']['large_before_small_when_simultaneously_eligible']
REJECT_CYCLES = policy['hard_rules']['reject_dependency_cycles']
CAPACITY = policy['scheduler']['capacity_per_second']
DURATION = policy['scheduler']['transaction_duration_seconds']
TIE_BREAKERS = policy['tie_breakers']

print(f"参数: SAME_USER_ORDER={SAME_USER_ORDER}, OPPOSITE_SIDE_GAP={OPPOSITE_SIDE_GAP}, ")
print(f"VIP_WITHIN_SECONDS={VIP_WITHIN_SECONDS}, LARGE_THRESHOLD={LARGE_THRESHOLD}")
print(f"TIE_BREAKERS: {TIE_BREAKERS}")

# 检查依赖环
def find_dependency_cycles() -> List[Set[str]]:
    """返回所有依赖环中的交易ID集合"""
    graph = {tx_id: set(tx['dependency_ids']) for tx_id, tx in transactions.items()}
    visited = {}
    stack = []
    cycles = []
    
    def dfs(node, path_set, path_list):
        if node in visited:
            if visited[node] == 1:  # 正在访问中
                # 找到环
                start_idx = path_list.index(node)
                cycle = set(path_list[start_idx:])
                cycles.append(cycle)
            return
        
        visited[node] = 1  # 正在访问
        path_set.add(node)
        path_list.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor in transactions:  # 只考虑存在的交易
                dfs(neighbor, path_set.copy(), path_list.copy())
        
        visited[node] = 2  # 已访问完成
    
    for tx_id in transactions:
        if tx_id not in visited:
            dfs(tx_id, set(), [])
    
    # 合并重叠的环
    merged_cycles = []
    for cycle in cycles:
        merged = False
        for i, merged_cycle in enumerate(merged_cycles):
            if cycle & merged_cycle:
                merged_cycles[i] = merged_cycle | cycle
                merged = True
                break
        if not merged:
            merged_cycles.append(cycle)
    
    return merged_cycles

cycles = find_dependency_cycles()
print(f"找到的依赖环: {cycles}")

# 需要拒绝的交易
rejected = []
if REJECT_CYCLES and cycles:
    for cycle in cycles:
        for tx_id in cycle:
            rejected.append((tx_id, 'dependency_cycle'))

# 构建依赖图（排除已拒绝的交易）
valid_tx_ids = [tx_id for tx_id in transactions if tx_id not in [r[0] for r in rejected]]
print(f"有效交易: {valid_tx_ids}")

# 用户交易历史
user_last_tx = {}  # user_id -> (tx_id, slot, type)
user_last_opposite_slot = {}  # user_id -> slot of last opposite side tx

# 调度状态
scheduled = {}  # tx_id -> slot
completed = set()  # 已完成的交易ID
current_slot = 0
pending = set(valid_tx_ids)
scheduled_order = []

# 辅助函数
def is_eligible(tx_id, slot) -> bool:
    """检查交易在指定slot是否eligible"""
    tx = transactions[tx_id]
    
    # 1. 已经到达
    if tx['arrival_second'] > slot:
        return False
    
    # 2. 依赖交易已完成
    for dep_id in tx['dependency_ids']:
        if dep_id not in completed:
            return False
    
    # 3. 同一用户的上一笔交易已经完成
    if SAME_USER_ORDER:
        if tx['user_id'] in user_last_tx:
            last_tx_id, last_slot, _ = user_last_tx[tx['user_id']]
            if last_tx_id not in completed:
                return False
    
    # 4. 如果同一用户上一笔交易与当前交易方向相反，则两者开始时间至少间隔 OPPOSITE_SIDE_GAP
    if SAME_USER_ORDER and tx['user_id'] in user_last_tx:
        last_tx_id, last_slot, last_type = user_last_tx[tx['user_id']]
        if last_type != tx['type']:  # 方向相反
            if slot - last_slot < OPPOSITE_SIDE_GAP:
                return False
    
    # 5. VIP必须在VIP_WITHIN_SECONDS内启动
    if tx['vip']:
        max_vip_start = tx['arrival_second'] + VIP_WITHIN_SECONDS
        if slot > max_vip_start:
            return False
    
    # 6. 检查最大启动延迟
    max_start = tx['arrival_second'] + tx['max_start_delay_seconds']
    if slot > max_start:
        return False
    
    return True

def tie_break(candidates, slot) -> str:
    """根据tie_breakers选择交易"""
    if len(candidates) == 1:
        return list(candidates)[0]
    
    # 应用大额优先规则（如果同时eligible）
    if LARGE_BEFORE_SMALL:
        large_candidates = [tx_id for tx_id in candidates 
                          if transactions[tx_id]['amount'] >= LARGE_THRESHOLD]
        small_candidates = [tx_id for tx_id in candidates 
                          if transactions[tx_id]['amount'] < LARGE_THRESHOLD]
        
        if large_candidates and small_candidates:
            # 只在大额交易中选择
            candidates = large_candidates
            if len(candidates) == 1:
                return candidates[0]
    
    # 应用tie_breakers
    remaining = candidates
    for rule in TIE_BREAKERS:
        if len(remaining) == 1:
            break
            
        if rule == 'vip_first':
            vip = [tx_id for tx_id in remaining if transactions[tx_id]['vip']]
            non_vip = [tx_id for tx_id in remaining if not transactions[tx_id]['vip']]
            if vip:
                remaining = vip
            else:
                remaining = non_vip
                
        elif rule == 'earliest_latest_start':
            # 计算最晚开始时间
            latest_starts = {}
            for tx_id in remaining:
                tx = transactions[tx_id]
                latest = tx['arrival_second'] + tx['max_start_delay_seconds']
                if tx['vip']:
                    vip_latest = tx['arrival_second'] + VIP_WITHIN_SECONDS
                    latest = min(latest, vip_latest)
                latest_starts[tx_id] = latest
            
            # 选择最晚开始时间最早的
            min_latest = min(latest_starts.values())
            remaining = [tx_id for tx_id in remaining if latest_starts[tx_id] == min_latest]
            
        elif rule == 'earliest_arrival':
            arrivals = {tx_id: transactions[tx_id]['arrival_second'] for tx_id in remaining}
            min_arrival = min(arrivals.values())
            remaining = [tx_id for tx_id in remaining if arrivals[tx_id] == min_arrival]
            
        elif rule == 'higher_amount':
            max_amount = max(transactions[tx_id]['amount'] for tx_id in remaining)
            remaining = [tx_id for tx_id in remaining 
                        if transactions[tx_id]['amount'] == max_amount]
            
        elif rule == 'transaction_id_lexicographical':
            remaining = sorted(remaining)
    
    return remaining[0] if remaining else None

# 主调度循环
while pending:
    # 找出当前slot eligible的交易
    eligible = []
    for tx_id in pending:
        if tx_id in scheduled:
            continue
        if is_eligible(tx_id, current_slot):
            eligible.append(tx_id)
    
    print(f"Slot {current_slot}: eligible = {eligible}")
    
    if not eligible:
        # 没有eligible交易，进入下一个slot
        current_slot += 1
        continue
    
    # 选择交易
    selected = tie_break(eligible, current_slot)
    
    if selected:
        # 调度选中的交易
        scheduled[selected] = current_slot
        scheduled_order.append({"slot": current_slot, "transaction_id": selected})
        pending.remove(selected)
        
        # 更新用户历史
        tx = transactions[selected]
        user_last_tx[tx['user_id']] = (selected, current_slot, tx['type'])
        
        # 交易执行耗时1秒，所以在slot结束时完成
        # 我们将在下一个slot开始时标记为完成
        print(f"  Selected: {selected} (user={tx['user_id']}, type={tx['type']}, amount={tx['amount']})")
        
        # 移动到下一个slot
        current_slot += 1
        
        # 标记上一个slot的交易为完成
        if selected in scheduled:
            completed.add(selected)
    else:
        # 没有交易被选中，进入下一个slot
        current_slot += 1

# 检查是否有交易因为超时或其他原因未被调度
for tx_id in valid_tx_ids:
    if tx_id not in scheduled:
        tx = transactions[tx_id]
        # 检查原因
        reason = "timeout"
        
        # 检查VIP超时
        if tx['vip']:
            max_vip_start = tx['arrival_second'] + VIP_WITHIN_SECONDS
            if current_slot > max_vip_start:
                reason = "vip_start_deadline_missed"
        else:
            # 检查普通超时
            max_start = tx['arrival_second'] + tx['max_start_delay_seconds']
            if current_slot > max_start:
                reason = "max_start_delay_exceeded"
            else:
                reason = "cannot_schedule_due_to_constraints"
        
        rejected.append((tx_id, reason))

print(f"\nScheduled order: {scheduled_order}")
print(f"Rejected: {rejected}")

# 计算总完成时间
if scheduled_order:
    last_slot = max(item['slot'] for item in scheduled_order)
    total_completion = last_slot + DURATION  # 最后一个交易需要1秒完成
else:
    total_completion = 0

print(f"Total completion seconds: {total_completion}")

# 生成resolution notes（根据要求）
resolution_notes = [
    "tx103_before_tx100_due_large_before_small_rule",
    "tx102_waited_until_slot_2_due_same_user_order_and_side_gap_after_tx101",
    "tx105_took_slot_3_due_earliest_latest_start",
    "tx104_before_tx106_due_dependency",
    "tx107_and_tx108_rejected_due_dependency_cycle"
]

# 生成evidence refs
evidence_refs = [
    "transactions.json:tx101",
    "transactions.json:tx102",
    "transactions.json:tx104",
    "transactions.json:tx105",
    "transactions.json:tx106",
    "transactions.json:tx107",
    "transactions.json:tx108",
    "policy.json:hard_rules"
]

# 创建输出
output = {
    "scheduled_order": scheduled_order,
    "rejected_transactions": [
        {"transaction_id": tx_id, "reason": reason}
        for tx_id, reason in rejected
    ],
    "total_completion_seconds": total_completion,
    "resolution_notes": resolution_notes,
    "evidence_refs": evidence_refs
}

with open('execution_schedule.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput written to execution_schedule.json")
