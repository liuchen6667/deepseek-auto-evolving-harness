import json
import itertools

# 读取数据
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

# 从scoring_policy.yaml中提取权重
perf_weight = 10
budget_div = 10
schedule_weight = 5
risk_weight = 3

# 基线分数计算
baseline_score = (baseline['performance_multiplier'] * perf_weight +
                 baseline['budget_overrun_pct'] / budget_div +
                 baseline['schedule_delay_months'] * schedule_weight +
                 baseline['risk_points'] * risk_weight)

# 创建决策映射
decision_map = {}
for d in decisions:
    decision_map[d['decision_id']] = d

# 计算所有3个决策组合
all_decisions = list(decision_map.keys())
best_combination = None
best_score = float('inf')  # 分数越低越好
best_improvement = 0

for combo in itertools.combinations(all_decisions, 3):
    # 计算总delta
    total_delta = {
        'performance_multiplier': 0,
        'budget_overrun_pct': 0,
        'schedule_delay_months': 0,
        'risk_points': 0
    }
    
    for decision_id in combo:
        delta = decision_map[decision_id]['delta']
        total_delta['performance_multiplier'] += delta['performance_multiplier']
        total_delta['budget_overrun_pct'] += delta['budget_overrun_pct']
        total_delta['schedule_delay_months'] += delta['schedule_delay_months']
        total_delta['risk_points'] += delta['risk_points']
    
    # 计算新值
    new_perf = baseline['performance_multiplier'] + total_delta['performance_multiplier']
    new_budget = baseline['budget_overrun_pct'] + total_delta['budget_overrun_pct']
    new_schedule = baseline['schedule_delay_months'] + total_delta['schedule_delay_months']
    new_risk = baseline['risk_points'] + total_delta['risk_points']
    
    # 计算新分数
    new_score = (new_perf * perf_weight +
                new_budget / budget_div +
                new_schedule * schedule_weight +
                new_risk * risk_weight)
    
    improvement = baseline_score - new_score
    
    # 检查是否更好
    if new_score < best_score:
        best_score = new_score
        best_improvement = improvement
        best_combination = combo
    elif new_score == best_score:
        # 根据tie-break规则：字母序最小的决策ID排序
        # 需要比较排序后的决策ID
        current_sorted = sorted(combo)
        best_sorted = sorted(best_combination)
        
        # 比较字母序
        if current_sorted < best_sorted:
            best_score = new_score
            best_improvement = improvement
            best_combination = combo

print(f"Best combination: {best_combination}")
print(f"Best score: {best_score}")
print(f"Improvement: {best_improvement}")

# 计算组合的投影值
if best_combination:
    total_delta = {
        'performance_multiplier': 0,
        'budget_overrun_pct': 0,
        'schedule_delay_months': 0,
        'risk_points': 0
    }
    
    for decision_id in best_combination:
        delta = decision_map[decision_id]['delta']
        total_delta['performance_multiplier'] += delta['performance_multiplier']
        total_delta['budget_overrun_pct'] += delta['budget_overrun_pct']
        total_delta['schedule_delay_months'] += delta['schedule_delay_months']
        total_delta['risk_points'] += delta['risk_points']
    
    new_perf = baseline['performance_multiplier'] + total_delta['performance_multiplier']
    new_budget = baseline['budget_overrun_pct'] + total_delta['budget_overrun_pct']
    new_schedule = baseline['schedule_delay_months'] + total_delta['schedule_delay_months']
    new_risk = baseline['risk_points'] + total_delta['risk_points']
    
    print(f"\nCombined projection:")
    print(f"  performance_multiplier: {new_perf}")
    print(f"  budget_overrun_pct: {new_budget}")
    print(f"  schedule_delay_months: {new_schedule}")
    print(f"  risk_points: {new_risk}")
    print(f"  score: {best_score}")
