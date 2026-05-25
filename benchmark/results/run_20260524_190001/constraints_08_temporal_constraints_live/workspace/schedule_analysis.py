import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class Transaction:
    id: str
    user_id: str
    type: str  # 'buy' or 'sell'
    amount: int
    arrival_second: int
    max_start_delay_seconds: int
    vip: bool
    dependency_ids: List[str]
    
    @property
    def latest_start(self):
        return self.arrival_second + self.max_start_delay_seconds
    
    @property
    def is_large(self):
        return self.amount >= 10000

# 读取数据
with open('transactions.json', 'r') as f:
    tx_data = json.load(f)

with open('policy.json', 'r') as f:
    policy_data = json.load(f)

# 创建交易对象
transactions: Dict[str, Transaction] = {}
for tx in tx_data['transactions']:
    transactions[tx['id']] = Transaction(
        id=tx['id'],
        user_id=tx['user_id'],
        type=tx['type'],
        amount=tx['amount'],
        arrival_second=tx['arrival_second'],
        max_start_delay_seconds=tx['max_start_delay_seconds'],
        vip=tx['vip'],
        dependency_ids=tx['dependency_ids']
    )

# 检查依赖环
def find_cycle() -> List[str]:
    visited = set()
    rec_stack = set()
    cycle_nodes = []
    
    def dfs(node: str, path: List[str]):
        nonlocal cycle_nodes
        if node in rec_stack:
            # 找到环
            start_idx = path.index(node)
            cycle_nodes = path[start_idx:]
            return True
        if node in visited:
            return False
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for dep in transactions[node].dependency_ids:
            if dep in transactions:  # 确保依赖存在
                if dfs(dep, path.copy()):
                    return True
        
        rec_stack.remove(node)
        path.pop()
        return False
    
    for tx_id in transactions:
        if tx_id not in visited:
            if dfs(tx_id, []):
                return cycle_nodes
    return []

cycle = find_cycle()
print(f"依赖环: {cycle}")

# 移除环中的交易
remaining_txs = {tx_id: tx for tx_id, tx in transactions.items() if tx_id not in cycle}
print(f"剩余交易: {list(remaining_txs.keys())}")

# 获取策略参数
hard_rules = policy_data['hard_rules']
tie_breakers = policy_data['tie_breakers']
same_user_opposite_side_gap = hard_rules['same_user_opposite_side_gap_seconds']
vip_start_within = hard_rules['vip_start_within_seconds']
large_threshold = hard_rules['large_amount_threshold']
large_before_small = hard_rules['large_before_small_when_simultaneously_eligible']

# 模拟调度
slot = 0
scheduled = []  # (slot, tx_id)
completed = set()
user_last_tx: Dict[str, Tuple[int, str]] = {}  # user_id -> (slot, type)

# 跟踪每笔交易的状态
tx_status = {tx_id: {
    'eligible_at': None,  # 最早合格时间
    'last_eligible_slot': None,  # 最晚启动时间
    'scheduled_slot': None,
    'completed_slot': None
} for tx_id in remaining_txs}

# 计算每笔交易的最晚启动时间
for tx_id, tx in remaining_txs.items():
    tx_status[tx_id]['last_eligible_slot'] = tx.latest_start

print("\n交易详情:")
for tx_id, tx in remaining_txs.items():
    print(f"{tx_id}: user={tx.user_id}, type={tx.type}, amount={tx.amount}, "
          f"arrival={tx.arrival_second}, latest={tx.latest_start}, vip={tx.vip}, "
          f"large={tx.is_large}, deps={tx.dependency_ids}")

print("\n开始调度:")
while True:
    # 找出当前slot的合格交易
    eligible = []
    for tx_id, tx in remaining_txs.items():
        if tx_status[tx_id]['scheduled_slot'] is not None:
            continue  # 已调度
            
        # 检查是否已到达
        if tx.arrival_second > slot:
            continue
            
        # 检查依赖是否完成
        deps_met = True
        for dep_id in tx.dependency_ids:
            if dep_id in remaining_txs and tx_status[dep_id]['completed_slot'] is None:
                deps_met = False
                break
        if not deps_met:
            continue
            
        # 检查同一用户上一笔交易
        if tx.user_id in user_last_tx:
            last_slot, last_type = user_last_tx[tx.user_id]
            # 同一用户顺序执行
            if last_slot + 1 > slot:
                continue
            # 方向相反时检查间隔
            if last_type != tx.type:
                if slot < last_slot + same_user_opposite_side_gap:
                    continue
        
        # 检查VIP时间约束
        if tx.vip and slot > tx.arrival_second + vip_start_within:
            continue  # VIP超时，但可能在其他slot合格
            
        eligible.append(tx_id)
    
    print(f"\nSlot {slot} 合格交易: {eligible}")
    
    if not eligible:
        # 检查是否所有交易都已调度或无法调度
        all_done = all(tx_status[tx_id]['scheduled_slot'] is not None for tx_id in remaining_txs)
        if all_done:
            break
        # 检查是否有交易还能在未来合格
        future_possible = False
        for tx_id, tx in remaining_txs.items():
            if tx_status[tx_id]['scheduled_slot'] is None:
                if tx.arrival_second <= slot and tx.latest_start >= slot:
                    # 还有交易在当前slot合格但被约束阻挡
                    pass
                elif tx.latest_start > slot:
                    future_possible = True
        
        if not future_possible:
            break
            
        slot += 1
        continue
    
    # 应用大额优先规则
    if large_before_small and len(eligible) > 1:
        large_txs = [tx_id for tx_id in eligible if remaining_txs[tx_id].is_large]
        small_txs = [tx_id for tx_id in eligible if not remaining_txs[tx_id].is_large]
        
        if large_txs and small_txs:
            print(f"  大额优先: 大额={large_txs}, 小额={small_txs}")
            eligible = large_txs  # 只考虑大额交易
    
    # 应用平局打破规则
    if len(eligible) > 1:
        for rule in tie_breakers:
            if rule == 'vip_first':
                vip_txs = [tx_id for tx_id in eligible if remaining_txs[tx_id].vip]
                non_vip_txs = [tx_id for tx_id in eligible if not remaining_txs[tx_id].vip]
                if vip_txs and non_vip_txs:
                    eligible = vip_txs
                    print(f"  VIP优先: {eligible}")
                    if len(eligible) == 1:
                        break
            
            elif rule == 'earliest_latest_start':
                # 选择最晚启动时间最早的
                min_latest = min(tx_status[tx_id]['last_eligible_slot'] for tx_id in eligible)
                eligible = [tx_id for tx_id in eligible if tx_status[tx_id]['last_eligible_slot'] == min_latest]
                print(f"  最早最晚启动: {eligible} (最晚={min_latest})")
                if len(eligible) == 1:
                    break
            
            elif rule == 'earliest_arrival':
                min_arrival = min(remaining_txs[tx_id].arrival_second for tx_id in eligible)
                eligible = [tx_id for tx_id in eligible if remaining_txs[tx_id].arrival_second == min_arrival]
                print(f"  最早到达: {eligible} (到达={min_arrival})")
                if len(eligible) == 1:
                    break
            
            elif rule == 'higher_amount':
                max_amount = max(remaining_txs[tx_id].amount for tx_id in eligible)
                eligible = [tx_id for tx_id in eligible if remaining_txs[tx_id].amount == max_amount]
                print(f"  更高金额: {eligible} (金额={max_amount})")
                if len(eligible) == 1:
                    break
            
            elif rule == 'transaction_id_lexicographical':
                eligible = [min(eligible)]
                print(f"  字典序: {eligible}")
                break
    
    # 调度选中的交易
    selected = eligible[0]
    tx = remaining_txs[selected]
    
    scheduled.append((slot, selected))
    tx_status[selected]['scheduled_slot'] = slot
    tx_status[selected]['completed_slot'] = slot + 1  # 执行耗时1秒
    
    # 更新用户最后交易
    user_last_tx[tx.user_id] = (slot, tx.type)
    
    print(f"  调度: {selected} at slot {slot}")
    
    # 移动到下一个slot
    slot += 1

print("\n调度结果:")
for s, tx_id in scheduled:
    print(f"  Slot {s}: {tx_id}")

print("\n交易状态:")
for tx_id in remaining_txs:
    status = tx_status[tx_id]
    print(f"  {tx_id}: scheduled={status['scheduled_slot']}, completed={status['completed_slot']}")

# 检查是否有交易未调度但应该被拒绝
rejected = []
for tx_id, tx in remaining_txs.items():
    if tx_status[tx_id]['scheduled_slot'] is None:
        # 检查原因
        if tx.vip and tx.arrival_second + vip_start_within < slot:
            rejected.append((tx_id, "vip_timeout"))
        elif tx.latest_start < slot:
            rejected.append((tx_id, "latest_start_passed"))
        else:
            # 其他原因（如依赖未满足但依赖交易被拒绝）
            rejected.append((tx_id, "cannot_schedule"))

print("\n应拒绝的交易:")
for tx_id, reason in rejected:
    print(f"  {tx_id}: {reason}")

# 添加依赖环中的交易
for tx_id in cycle:
    rejected.append((tx_id, "dependency_cycle"))

print("\n最终拒绝列表（含依赖环）:")
for tx_id, reason in rejected:
    print(f"  {tx_id}: {reason}")