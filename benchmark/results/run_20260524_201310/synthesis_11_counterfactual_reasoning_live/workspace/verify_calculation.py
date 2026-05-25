import json
import yaml

def calculate_score(performance_multiplier, budget_overrun_pct, schedule_delay_months, risk_points):
    with open('scoring_policy.yaml', 'r') as f:
        policy = yaml.safe_load(f)
    
    weight_perf = policy['score_formula']['performance_multiplier_weight']
    divisor_budget = policy['score_formula']['budget_overrun_divisor']
    weight_schedule = policy['score_formula']['schedule_delay_month_weight']
    weight_risk = policy['score_formula']['risk_point_weight']
    
    score = (performance_multiplier * weight_perf) - \
            (budget_overrun_pct / divisor_budget) - \
            (schedule_delay_months * weight_schedule) - \
            (risk_points * weight_risk)
    
    return score

# 读取基线数据
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

print(f"Baseline: {baseline}")
baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)
print(f"Baseline score: {baseline_score}")

# 读取决策矩阵
with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

# 找到特定决策的delta
deltas = {}
for decision in decisions:
    if decision['decision_id'] in ['stack', 'testing', 'delivery']:
        deltas[decision['decision_id']] = decision['delta']
        print(f"{decision['decision_id']} delta: {decision['delta']}")

# 计算组合delta
combo_delta = {
    'performance_multiplier': 0,
    'budget_overrun_pct': 0,
    'schedule_delay_months': 0,
    'risk_points': 0
}

for decision_id in ['stack', 'testing', 'delivery']:
    for key in combo_delta:
        combo_delta[key] += deltas[decision_id][key]

print(f"\nCombined delta: {combo_delta}")

# 计算组合后的指标
combo_metrics = {
    'performance_multiplier': baseline['performance_multiplier'] + combo_delta['performance_multiplier'],
    'budget_overrun_pct': baseline['budget_overrun_pct'] + combo_delta['budget_overrun_pct'],
    'schedule_delay_months': baseline['schedule_delay_months'] + combo_delta['schedule_delay_months'],
    'risk_points': baseline['risk_points'] + combo_delta['risk_points']
}

print(f"\nCombined metrics: {combo_metrics}")

# 计算组合分数
combo_score = calculate_score(
    combo_metrics['performance_multiplier'],
    combo_metrics['budget_overrun_pct'],
    combo_metrics['schedule_delay_months'],
    combo_metrics['risk_points']
)

print(f"Combined score: {combo_score}")
print(f"Improvement: {combo_score - baseline_score}")

# 验证individual scores
print("\nVerifying individual scores:")
for decision in decisions:
    if decision['decision_id'] in ['stack', 'testing', 'delivery']:
        perf = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
        budget = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
        schedule = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
        risk = baseline['risk_points'] + decision['delta']['risk_points']
        
        score = calculate_score(perf, budget, schedule, risk)
        improvement = score - baseline_score
        print(f"{decision['decision_id']}: score={score}, improvement={improvement}")