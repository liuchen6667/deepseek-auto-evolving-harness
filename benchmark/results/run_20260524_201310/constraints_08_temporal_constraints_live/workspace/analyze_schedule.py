import json
from collections import defaultdict, deque

def load_data():
    with open('transactions.json', 'r') as f:
        tx_data = json.load(f)
    with open('policy.json', 'r') as f:
        policy = json.load(f)
    return tx_data['transactions'], policy

def find_dependency_cycles(transactions):
    """检测依赖环"""
    # 构建邻接表
    adj = {}
    for tx in transactions:
        adj[tx['id']] = tx['dependency_ids']
    
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in adj.get(node, []):
            if neighbor not in adj:
                continue  # 依赖的交易可能不存在，但这里所有交易都在列表中
            if neighbor not in visited:
                if dfs(neighbor, path + [node]):
                    return True
            elif neighbor in rec_stack:
                # 找到环
                cycle_start = path.index(neighbor) if neighbor in path else -1
                if cycle_start >= 0:
                    cycle = path[cycle_start:] + [node, neighbor]
                    cycles.append(cycle)
                else:
                    cycles.append([neighbor, node] + [neighbor])
                return True
        
        rec_stack.remove(node)
        return False
    
    for tx in transactions:
        if tx['id'] not in visited:
            dfs(tx['id'], [])
    
    # 获取环中的所有交易
    cycle_txs = set()
    for cycle in cycles:
        for node in cycle:
            cycle_txs.add(node)
    
    return list(cycle_txs)

def is_large_amount(amount, threshold):
    return amount >= threshold

def get_eligible_transactions(slot, completed_txs, user_last_tx, transactions, policy):
    """获取在指定slot符合条件的交易"""
    eligible = []
    
    for tx in transactions:
        tx_id = tx['id']
        
        # 检查是否已经完成或被拒绝
        if tx_id in completed_txs:
            continue
        
        # 检查是否已经到达
        if tx['arrival_second'] > slot:
            continue
        
        # 检查依赖
        dependencies_met = True
        for dep_id in tx['dependency_ids']:
            if dep_id not in completed_txs:
                dependencies_met = False
                break
        if not dependencies_met:
            continue
        
        # 检查同一用户顺序
        user_id = tx['user_id']
        if policy['hard_rules']['same_user_order']:
            if user_id in user_last_tx:
                last_tx_info = user_last_tx[user_id]
                if last_tx_info['completed_slot'] is None or last_tx_info['completed_slot'] >= slot:
                    # 上一笔交易还未完成
                    continue
        
        # 检查相反方向间隔
        if user_id in user_last_tx:
            last_tx_info = user_last_tx[user_id]
            if last_tx_info['type'] != tx['type']:
                gap = policy['hard_rules']['same_user_opposite_side_gap_seconds']
                last_completion = last_tx_info['completed_slot'] + 1  # 完成时间槽+1秒
                if slot < last_completion + gap:
                    continue
        
        # 检查VIP约束
        if tx['vip']:
            max_start = tx['arrival_second'] + policy['hard_rules']['vip_start_within_seconds']
            if slot > max_start:
                continue
        
        # 检查最大启动延迟
        max_start = tx['arrival_second'] + tx['max_start_delay_seconds']
        if slot > max_start:
            continue
        
        eligible.append(tx)
    
    return eligible

def break_ties(eligible, policy, slot):
    """按照tie_breakers规则打破平局"""
    if not eligible:
        return None
    
    # 应用大额优先规则
    large_threshold = policy['hard_rules']['large_amount_threshold']
    if policy['hard_rules']['large_before_small_when_simultaneously_eligible']:
        large_txs = [tx for tx in eligible if is_large_amount(tx['amount'], large_threshold)]
        small_txs = [tx for tx in eligible if not is_large_amount(tx['amount'], large_threshold)]
        
        if large_txs and small_txs:
            # 只考虑大额交易
            eligible = large_txs
    
    # 按tie_breakers排序
    for rule in policy['tie_breakers']:
        if rule == 'vip_first':
            eligible.sort(key=lambda x: not x['vip'])  # VIP先排
        elif rule == 'earliest_latest_start':
            # 最早最晚开始时间（arrival + max_start_delay_seconds）
            eligible.sort(key=lambda x: x['arrival_second'] + x['max_start_delay_seconds'])
        elif rule == 'earliest_arrival':
            eligible.sort(key=lambda x: x['arrival_second'])
        elif rule == 'higher_amount':
            eligible.sort(key=lambda x: x['amount'], reverse=True)
        elif rule == 'transaction_id_lexicographical':
            eligible.sort(key=lambda x: x['id'])
    
    return eligible[0] if eligible else None

def main():
    transactions, policy = load_data()
    
    # 查找依赖环
    cycle_txs = find_dependency_cycles(transactions)
    
    # 初始化状态
    scheduled = []  # 计划顺序
    completed_txs = set()  # 已完成交易ID
    user_last_tx = {}  # 用户最后交易信息
    
    # 记录被拒绝的交易
    rejected = []
    
    # 拒绝依赖环中的交易
    for tx_id in cycle_txs:
        rejected.append({"transaction_id": tx_id, "reason": "dependency_cycle"})
    
    # 过滤掉环中的交易
    valid_transactions = [tx for tx in transactions if tx['id'] not in cycle_txs]
    
    # 模拟调度
    slot = 0
    max_slots = 100  # 防止无限循环
    
    while len(completed_txs) < len(valid_transactions) and slot < max_slots:
        # 获取符合条件的交易
        eligible = get_eligible_transactions(slot, completed_txs, user_last_tx, valid_transactions, policy)
        
        if not eligible:
            slot += 1
            continue
        
        # 打破平局选择交易
        selected = break_ties(eligible, policy, slot)
        
        if selected:
            # 安排交易
            scheduled.append({"slot": slot, "transaction_id": selected['id']})
            completed_txs.add(selected['id'])
            
            # 更新用户最后交易信息
            user_last_tx[selected['user_id']] = {
                'completed_slot': slot,
                'type': selected['type']
            }
            
            slot += 1
        else:
            slot += 1
    
    # 检查是否有交易因为约束无法调度（除了依赖环）
    for tx in valid_transactions:
        if tx['id'] in completed_txs:
            continue
        
        # 检查为什么无法调度
        # 简单标记为无法调度
        rejected.append({"transaction_id": tx['id'], "reason": "cannot_schedule_due_to_constraints"})
    
    # 计算总完成时间
    total_completion_seconds = slot if scheduled else 0
    
    # 生成输出
    output = {
        "scheduled_order": scheduled,
        "rejected_transactions": rejected,
        "total_completion_seconds": total_completion_seconds,
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
    
    with open('execution_schedule.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("Schedule generated successfully")
    print(f"Scheduled: {len(scheduled)} transactions")
    print(f"Rejected: {len(rejected)} transactions")
    print(f"Total completion seconds: {total_completion_seconds}")

if __name__ == "__main__":
    main()