import json
import yaml

def calculate_score(performance_multiplier, budget_overrun_pct, schedule_delay_months, risk_points):
    # 从scoring_policy.yaml读取权重
    with open('scoring_policy.yaml', 'r') as f:
        policy = yaml.safe_load(f)
    
    weight_perf = policy['score_formula']['performance_multiplier_weight']
    divisor_budget = policy['score_formula']['budget_overrun_divisor']
    weight_schedule = policy['score_formula']['schedule_delay_month_weight']
    weight_risk = policy['score_formula']['risk_point_weight']
    
    # 计算分数
    score = (performance_multiplier * weight_perf) - \
            (budget_overrun_pct / divisor_budget) - \
            (schedule_delay_months * weight_schedule) - \
            (risk_points * weight_risk)
    
    return score

# 读取基线数据
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)

print(f"Baseline score: {baseline_score}")
print(f"Baseline data: {baseline}")

# 读取决策矩阵
with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

print("\nIndividual decision evaluations:")
for decision in decisions:
    # 应用delta到基线
    perf = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
    budget = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
    schedule = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
    risk = baseline['risk_points'] + decision['delta']['risk_points']
    
    score = calculate_score(perf, budget, schedule, risk)
    improvement = score - baseline_score
    
    print(f"{decision['decision_id']} ({decision['alternative']}): score={score:.2f}, improvement={improvement:.2f}")