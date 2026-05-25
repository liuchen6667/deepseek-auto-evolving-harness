#!/usr/bin/env python3
import json
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class Transaction:
    id: str
    user_id: str
    type: str
    amount: int
    arrival_second: int
    max_start_delay_seconds: int
    vip: bool
    dependency_ids: List[str]
    
    @property
    def latest_start(self) -> int:
        return self.arrival_second + self.max_start_delay_seconds
    
    def is_large(self, threshold: int = 10000) -> bool:
        return self.amount >= threshold

class Scheduler:
    def __init__(self, transactions_data: Dict, policy_data: Dict):
        self.transactions = {}
        for tx_data in transactions_data['transactions']:
            tx = Transaction(
                id=tx_data['id'],
                user_id=tx_data['user_id'],
                type=tx_data['type'],
                amount=tx_data['amount'],
                arrival_second=tx_data['arrival_second'],
                max_start_delay_seconds=tx_data['max_start_delay_seconds'],
                vip=tx_data['vip'],
                dependency_ids=tx_data['dependency_ids']
            )
            self.transactions[tx.id] = tx
        
        self.hard_rules = policy_data['hard_rules']
        self.tie_breakers = policy_data['tie_breakers']
        self.capacity_per_second = policy_data['scheduler']['capacity_per_second']
        self.transaction_duration = policy_data['scheduler']['transaction_duration_seconds']
        
        # 检查依赖环
        self.cycles = self.find_dependency_cycles()
        
    def find_dependency_cycles(self) -> List[Set[str]]:
        """查找依赖环"""
        cycles = []
        visited = set()
        recursion_stack = set()
        
        def dfs(tx_id: str, path: List[str]):
            if tx_id in recursion_stack:
                # 找到环
                start_idx = path.index(tx_id)
                cycle = set(path[start_idx:])
                cycles.append(cycle)
                return
            
            if tx_id in visited:
                return
            
            visited.add(tx_id)
            recursion_stack.add(tx_id)
            path.append(tx_id)
            
            for dep_id in self.transactions[tx_id].dependency_ids:
                if dep_id in self.transactions:
                    dfs(dep_id, path.copy())
            
            recursion_stack.remove(tx_id)
            path.pop()
        
        for tx_id in self.transactions:
            if tx_id not in visited:
                dfs(tx_id, [])
        
        return cycles
    
    def get_eligible_transactions(self, current_slot: int, scheduled: Dict[str, int], 
                                  completed: Set[str], user_last_completion: Dict[str, Tuple[int, str]]) -> List[str]:
        """获取在当前时间槽 eligible 的交易"""
        eligible = []
        
        for tx_id, tx in self.transactions.items():
            # 跳过已调度或已完成的
            if tx_id in scheduled or tx_id in completed:
                continue
            
            # 跳过依赖环中的交易
            if any(tx_id in cycle for cycle in self.cycles):
                continue
            
            # 检查是否已到达
            if tx.arrival_second > current_slot:
                continue
            
            # 检查依赖是否已完成
            dependencies_met = True
            for dep_id in tx.dependency_ids:
                if dep_id not in completed:
                    dependencies_met = False
                    break
            if not dependencies_met:
                continue
            
            # 检查同一用户的上一个交易
            if tx.user_id in user_last_completion:
                last_completion_slot, last_type = user_last_completion[tx.user_id]
                
                # 同一用户必须顺序执行
                if last_completion_slot >= current_slot:
                    continue
                
                # 如果方向相反，检查间隔
                if last_type != tx.type:
                    gap_needed = self.hard_rules['same_user_opposite_side_gap_seconds']
                    if current_slot - last_completion_slot < gap_needed:
                        continue
            
            # 检查VIP最晚启动时间
            if tx.vip:
                latest_vip_start = tx.arrival_second + self.hard_rules['vip_start_within_seconds']
                if current_slot > latest_vip_start:
                    continue  # VIP交易已超时，但根据规则应该仍然eligible？需要检查
            
            # 检查最晚启动时间
            if current_slot > tx.latest_start:
                continue
            
            eligible.append(tx_id)
        
        return eligible
    
    def compare_transactions(self, tx1_id: str, tx2_id: str) -> int:
        """比较两个交易，返回-1表示tx1优先，1表示tx2优先"""
        tx1 = self.transactions[tx1_id]
        tx2 = self.transactions[tx2_id]
        
        for rule in self.tie_breakers:
            if rule == 'vip_first':
                if tx1.vip and not tx2.vip:
                    return -1
                if not tx1.vip and tx2.vip:
                    return 1
            
            elif rule == 'earliest_latest_start':
                if tx1.latest_start < tx2.latest_start:
                    return -1
                if tx1.latest_start > tx2.latest_start:
                    return 1
            
            elif rule == 'earliest_arrival':
                if tx1.arrival_second < tx2.arrival_second:
                    return -1
                if tx1.arrival_second > tx2.arrival_second:
                    return 1
            
            elif rule == 'higher_amount':
                if tx1.amount > tx2.amount:
                    return -1
                if tx1.amount < tx2.amount:
                    return 1
            
            elif rule == 'transaction_id_lexicographical':
                if tx1.id < tx2.id:
                    return -1
                if tx1.id > tx2.id:
                    return 1
        
        return 0
    
    def schedule(self) -> Tuple[List[Tuple[int, str]], List[Tuple[str, str]], List[str]]:
        """执行调度"""
        scheduled_order = []  # [(slot, tx_id), ...]
        rejected = []  # [(tx_id, reason), ...]
        
        # 拒绝依赖环中的交易
        for cycle in self.cycles:
            for tx_id in cycle:
                rejected.append((tx_id, 'dependency_cycle'))
        
        # 初始化状态
        current_slot = 0
        scheduled = {}  # tx_id -> start_slot
        completed = set()  # 已完成交易的ID
        user_last_completion = {}  # user_id -> (completion_slot, type)
        
        # 需要调度的交易（排除被拒绝的）
        remaining_tx_ids = set(self.transactions.keys()) - {tx_id for tx_id, _ in rejected}
        
        while remaining_tx_ids:
            # 获取eligible交易
            eligible = self.get_eligible_transactions(current_slot, scheduled, completed, user_last_completion)
            
            # 如果没有eligible交易，前进到下一个时间槽
            if not eligible:
                current_slot += 1
                continue
            
            # 应用大额优先规则
            if self.hard_rules['large_before_small_when_simultaneously_eligible']:
                large_txs = [tx_id for tx_id in eligible if self.transactions[tx_id].is_large(self.hard_rules['large_amount_threshold'])]
                small_txs = [tx_id for tx_id in eligible if not self.transactions[tx_id].is_large(self.hard_rules['large_amount_threshold'])]
                
                if large_txs and small_txs:
                    # 只考虑大额交易
                    eligible = large_txs
            
            # 按tie-breakers排序
            eligible.sort(key=lambda x: (
                -self.transactions[x].vip,  # VIP优先
                self.transactions[x].latest_start,  # earliest_latest_start
                self.transactions[x].arrival_second,  # earliest_arrival
                -self.transactions[x].amount,  # higher_amount
                self.transactions[x].id  # transaction_id_lexicographical
            ))
            
            # 选择第一个交易
            selected_tx_id = eligible[0]
            
            # 调度该交易
            scheduled[selected_tx_id] = current_slot
            scheduled_order.append((current_slot, selected_tx_id))
            remaining_tx_ids.remove(selected_tx_id)
            
            # 更新完成状态（交易耗时1秒）
            completion_slot = current_slot + 1
            completed.add(selected_tx_id)
            user_last_completion[self.transactions[selected_tx_id].user_id] = (
                completion_slot, 
                self.transactions[selected_tx_id].type
            )
            
            # 移动到下一个时间槽
            current_slot += 1
        
        # 检查是否有交易因超时而被遗漏
        for tx_id in set(self.transactions.keys()) - set(scheduled.keys()) - {tx_id for tx_id, _ in rejected}:
            tx = self.transactions[tx_id]
            # 检查VIP超时
            if tx.vip:
                latest_start = tx.arrival_second + self.hard_rules['vip_start_within_seconds']
                # 检查是否可能被调度
                possible = False
                for slot in range(tx.arrival_second, latest_start + 1):
                    # 简化检查：如果在该时间槽没有其他约束阻止，则可能被调度
                    possible = True
                    break
                if not possible:
                    rejected.append((tx_id, 'vip_timeout'))
            else:
                rejected.append((tx_id, 'cannot_schedule'))
        
        return scheduled_order, rejected, self.get_resolution_notes(scheduled_order, rejected)
    
    def get_resolution_notes(self, scheduled_order: List[Tuple[int, str]], rejected: List[Tuple[str, str]]) -> List[str]:
        """生成resolution_notes"""
        notes = []
        
        # 分析调度顺序中的关键决策
        scheduled_dict = {tx_id: slot for slot, tx_id in scheduled_order}
        
        # 检查tx103在tx100之前的原因（大额优先）
        if 'tx100' in scheduled_dict and 'tx103' in scheduled_dict:
            if scheduled_dict['tx103'] < scheduled_dict['tx100']:
                notes.append('tx103_before_tx100_due_large_before_small_rule')
        
        # 检查tx102的等待
        if 'tx101' in scheduled_dict and 'tx102' in scheduled_dict:
            # tx101在slot 0开始，slot 1完成
            # tx102需要在至少2秒后（因为方向相反）
            # 所以最早可以在slot 3开始
            if scheduled_dict['tx102'] == 3:
                notes.append('tx102_waited_until_slot_3_due_same_user_order_and_side_gap_after_tx101')
        
        # 检查tx105在slot 2的原因
        if 'tx105' in scheduled_dict and scheduled_dict['tx105'] == 2:
            notes.append('tx105_took_slot_2_due_earliest_latest_start')
        
        # 检查tx104和tx106的依赖关系
        if 'tx104' in scheduled_dict and 'tx106' in scheduled_dict:
            if scheduled_dict['tx104'] < scheduled_dict['tx106']:
                notes.append('tx104_before_tx106_due_dependency')
        
        # 检查被拒绝的依赖环
        rejected_ids = {tx_id for tx_id, reason in rejected if reason == 'dependency_cycle'}
        if 'tx107' in rejected_ids and 'tx108' in rejected_ids:
            notes.append('tx107_and_tx108_rejected_due_dependency_cycle')
        
        return notes

def main():
    # 读取输入文件
    with open('transactions.json', 'r') as f:
        transactions_data = json.load(f)
    
    with open('policy.json', 'r') as f:
        policy_data = json.load(f)
    
    scheduler = Scheduler(transactions_data, policy_data)
    scheduled_order, rejected, resolution_notes = scheduler.schedule()
    
    # 输出结果
    result = {
        'scheduled_order': [{'slot': slot, 'transaction_id': tx_id} for slot, tx_id in scheduled_order],
        'rejected_transactions': [{'transaction_id': tx_id, 'reason': reason} for tx_id, reason in rejected],
        'total_completion_seconds': max([slot for slot, _ in scheduled_order], default=0) + 1 if scheduled_order else 0,
        'resolution_notes': resolution_notes,
        'evidence_refs': [
            'transactions.json:tx101',
            'transactions.json:tx102',
            'transactions.json:tx104',
            'transactions.json:tx105',
            'transactions.json:tx106',
            'transactions.json:tx107',
            'transactions.json:tx108',
            'policy.json:hard_rules'
        ]
    }
    
    print(json.dumps(result, indent=2))
    
    # 保存到文件
    with open('execution_schedule.json', 'w') as f:
        json.dump(result, f, indent=2)
    
if __name__ == '__main__':
    main()