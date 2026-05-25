import json

# 读取数据
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

with open('scoring_policy.yaml', 'r') as f:
    import yaml
    policy = yaml.safe_load(f)

# 提取权重
weights = policy['score_formula']
pm_weight = weights['performance_multiplier_weight']
budget_div = weights['budget_overrun_divisor']
schedule_weight = weights['schedule_delay_month_weight']
risk_weight = weights['risk_point_weight']

# 计算基线分数
def calculate_score(pm, budget, schedule, risk):
    return (pm * pm_weight) - (budget / budget_div) - (schedule * schedule_weight) - (risk * risk_weight)

baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)
print(f"Baseline score: {baseline_score}")

# 计算每个决策的改进
results = []
for decision in decisions:
    # 应用 delta
    new_pm = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
    new_budget = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
    new_schedule = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
    new_risk = baseline['risk_points'] + decision['delta']['risk_points']
    
    new_score = calculate_score(new_pm, new_budget, new_schedule, new_risk)
    improvement = new_score - baseline_score
    
    results.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': round(new_score, 2),
        'score_improvement': round(improvement, 2)
    })

# 按 improvement 降序排序
results.sort(key=lambda x: x['score_improvement'], reverse=True)

print("\nTop 3 individual changes:")
for i, r in enumerate(results[:3]):
    print(f"{i+1}. {r['decision_id']} -> {r['alternative']}: improvement = {r['score_improvement']}")

# 输出所有结果用于检查
print("\nAll results:")
for r in results:
    print(f"{r['decision_id']}: improvement = {r['score_improvement']}")

# 现在计算所有3个决策的组合
from itertools import combinations

decision_ids = [d['decision_id'] for d in decisions]
print(f"\nTotal decisions: {len(decision_ids)}")

# 创建决策映射
decision_map = {d['decision_id']: d for d in decisions}

best_score = float('-inf')
best_combination = None
best_projection = None

# 检查所有3个决策的组合
for combo in combinations(decision_ids, 3):
    # 线性叠加 delta
    total_delta = {
        'performance_multiplier': 0,
        'budget_overrun_pct': 0,
        'schedule_delay_months': 0,
        'risk_points': 0
    }
    
    for decision_id in combo:
        delta = decision_map[decision_id]['delta']
        for key in total_delta:
            total_delta[key] += delta[key]
    
    # 应用总 delta
    new_pm = baseline['performance_multiplier'] + total_delta['performance_multiplier']
    new_budget = baseline['budget_overrun_pct'] + total_delta['budget_overrun_pct']
    new_schedule = baseline['schedule_delay_months'] + total_delta['schedule_delay_months']
    new_risk = baseline['risk_points'] + total_delta['risk_points']
    
    new_score = calculate_score(new_pm, new_budget, new_schedule, new_risk)
    
    if new_score > best_score:
        best_score = new_score
        best_combination = sorted(combo)  # 按字母序排序
        best_projection = {
            'performance_multiplier': round(new_pm, 2),
            'budget_overrun_pct': round(new_budget),
            'schedule_delay_months': round(new_schedule),
            'risk_points': round(new_risk),
            'score': round(new_score, 2)
        }
    elif new_score == best_score:
        # 并列情况，按字母序最小的排序决策ID选择
        sorted_combo = sorted(combo)
        if best_combination is None or sorted_combo < best_combination:
            best_combination = sorted_combo
            best_projection = {
                'performance_multiplier': round(new_pm, 2),
                'budget_overrun_pct': round(new_budget),
                'schedule_delay_months': round(new_schedule),
                'risk_points': round(new_risk),
                'score': round(new_score, 2)
            }

print(f"\nBest 3-change combination: {best_combination}")
print(f"Projected score: {best_score}")
print(f"Projection: {best_projection}")

# 选择推荐
with open('recommendation_catalog.json', 'r') as f:
    recs = json.load(f)

recommendation_codes = recs['recommendation_codes']
# 按字母序排序
recommendation_codes.sort()
# 取前2个
selected_recs = recommendation_codes[:2]
print(f"\nSelected recommendations: {selected_recs}")