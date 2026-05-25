import json
import yaml
import itertools

# 加载数据
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

with open('scoring_policy.yaml', 'r') as f:
    policy = yaml.safe_load(f)

# 提取权重
w_pm = policy['score_formula']['performance_multiplier_weight']
d_bo = policy['score_formula']['budget_overrun_divisor']
w_sd = policy['score_formula']['schedule_delay_month_weight']
w_rp = policy['score_formula']['risk_point_weight']

# 基准指标
pm_base = baseline['performance_multiplier']
bo_base = baseline['budget_overrun_pct']
sd_base = baseline['schedule_delay_months']
rp_base = baseline['risk_points']

# 创建决策字典以便快速访问
decision_dict = {d['decision_id']: d for d in decisions}

# 生成所有3个决策的组合
decision_ids = list(decision_dict.keys())
combinations = list(itertools.combinations(decision_ids, 3))

best_score = float('-inf')
best_combinations = []  # 可能有多个组合分数相同
best_combined_projection = None

for combo in combinations:
    # 初始化增量总和
    delta_sum = {
        'performance_multiplier': 0.0,
        'budget_overrun_pct': 0,
        'schedule_delay_months': 0,
        'risk_points': 0
    }
    
    # 累加所有决策的增量
    for decision_id in combo:
        delta = decision_dict[decision_id]['delta']
        delta_sum['performance_multiplier'] += delta['performance_multiplier']
        delta_sum['budget_overrun_pct'] += delta['budget_overrun_pct']
        delta_sum['schedule_delay_months'] += delta['schedule_delay_months']
        delta_sum['risk_points'] += delta['risk_points']
    
    # 计算新指标
    new_pm = pm_base + delta_sum['performance_multiplier']
    new_bo = bo_base + delta_sum['budget_overrun_pct']
    new_sd = sd_base + delta_sum['schedule_delay_months']
    new_rp = rp_base + delta_sum['risk_points']
    
    # 计算新分数
    new_score = (new_pm * w_pm) - (new_bo / d_bo) - (new_sd * w_sd) - (new_rp * w_rp)
    
    # 检查是否是最佳组合
    if new_score > best_score:
        best_score = new_score
        best_combinations = [sorted(list(combo))]  # 按字母序排序
        best_combined_projection = {
            'performance_multiplier': new_pm,
            'budget_overrun_pct': new_bo,
            'schedule_delay_months': new_sd,
            'risk_points': new_rp,
            'score': new_score
        }
    elif abs(new_score - best_score) < 1e-10:  # 分数相同（考虑浮点误差）
        sorted_combo = sorted(list(combo))
        if sorted_combo not in best_combinations:
            best_combinations.append(sorted_combo)

print(f"Best score: {best_score}")
print(f"Number of combinations with best score: {len(best_combinations)}")

# 按tie-break规则排序：alphabetically_smallest_sorted_decision_ids
# 这意味着我们需要比较整个排序后的决策ID列表的字典序
best_combinations.sort()
print(f"Best combinations (sorted): {best_combinations}")

# 根据tie-break规则选择第一个（字典序最小）
best_combo = best_combinations[0]
print(f"Selected best combination (tie-break): {best_combo}")

# 重新计算选定组合的投影以确保精度
delta_sum = {
    'performance_multiplier': 0.0,
    'budget_overrun_pct': 0,
    'schedule_delay_months': 0,
    'risk_points': 0
}

for decision_id in best_combo:
    delta = decision_dict[decision_id]['delta']
    delta_sum['performance_multiplier'] += delta['performance_multiplier']
    delta_sum['budget_overrun_pct'] += delta['budget_overrun_pct']
    delta_sum['schedule_delay_months'] += delta['schedule_delay_months']
    delta_sum['risk_points'] += delta['risk_points']

new_pm = pm_base + delta_sum['performance_multiplier']
new_bo = bo_base + delta_sum['budget_overrun_pct']
new_sd = sd_base + delta_sum['schedule_delay_months']
new_rp = rp_base + delta_sum['risk_points']

# 重新计算分数
final_score = (new_pm * w_pm) - (new_bo / d_bo) - (new_sd * w_sd) - (new_rp * w_rp)

print(f"\nFinal combined projection:")
print(f"  performance_multiplier: {new_pm}")
print(f"  budget_overrun_pct: {new_bo}")
print(f"  schedule_delay_months: {new_sd}")
print(f"  risk_points: {new_rp}")
print(f"  score: {final_score}")