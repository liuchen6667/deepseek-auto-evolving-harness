import json
import yaml
import itertools

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

# 读取决策矩阵
with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)

# 存储决策数据
decision_data = {}
for decision in decisions:
    decision_data[decision['decision_id']] = {
        'alternative': decision['alternative'],
        'delta': decision['delta'],
        'score_improvement': None
    }
    
    # 计算单个决策的分数
    perf = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
    budget = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
    schedule = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
    risk = baseline['risk_points'] + decision['delta']['risk_points']
    
    score = calculate_score(perf, budget, schedule, risk)
    improvement = score - baseline_score
    decision_data[decision['decision_id']]['score_improvement'] = improvement
    decision_data[decision['decision_id']]['projected_score'] = score

# 获取所有决策ID
all_ids = list(decision_data.keys())
print(f"All decision IDs: {all_ids}")
print(f"Number of decisions: {len(all_ids)}")

# 生成所有可能的3个决策组合
all_combinations = list(itertools.combinations(all_ids, 3))
print(f"Number of 3-decision combinations: {len(all_combinations)}")

best_combination = None
best_score = float('-inf')
best_combination_data = None

for combo in all_combinations:
    # 计算组合后的指标
    perf_delta = 0
    budget_delta = 0
    schedule_delta = 0
    risk_delta = 0
    
    for decision_id in combo:
        perf_delta += decision_data[decision_id]['delta']['performance_multiplier']
        budget_delta += decision_data[decision_id]['delta']['budget_overrun_pct']
        schedule_delta += decision_data[decision_id]['delta']['schedule_delay_months']
        risk_delta += decision_data[decision_id]['delta']['risk_points']
    
    # 应用delta到基线
    perf = baseline['performance_multiplier'] + perf_delta
    budget = baseline['budget_overrun_pct'] + budget_delta
    schedule = baseline['schedule_delay_months'] + schedule_delta
    risk = baseline['risk_points'] + risk_delta
    
    score = calculate_score(perf, budget, schedule, risk)
    improvement = score - baseline_score
    
    # 存储组合数据
    combo_data = {
        'decision_ids': sorted(combo),  # 按字母序排序以便比较
        'score': score,
        'improvement': improvement,
        'metrics': {
            'performance_multiplier': perf,
            'budget_overrun_pct': budget,
            'schedule_delay_months': schedule,
            'risk_points': risk
        }
    }
    
    if score > best_score:
        best_score = score
        best_combination = combo
        best_combination_data = combo_data
    elif score == best_score:
        # 平局处理：按字母序最小的排序决策ID
        current_best_sorted = sorted(best_combination)
        new_combo_sorted = sorted(combo)
        
        # 比较字母序
        if new_combo_sorted < current_best_sorted:
            best_score = score
            best_combination = combo
            best_combination_data = combo_data

print(f"\nBest combination: {best_combination_data['decision_ids']}")
print(f"Best score: {best_score:.2f}")
print(f"Improvement: {best_combination_data['improvement']:.2f}")
print(f"Metrics: {best_combination_data['metrics']}")

# 输出前3名单个决策
print("\nTop 3 individual decisions:")
sorted_individual = sorted(decision_data.items(), key=lambda x: x[1]['score_improvement'], reverse=True)
for i, (decision_id, data) in enumerate(sorted_individual[:3]):
    print(f"{i+1}. {decision_id}: improvement={data['score_improvement']:.2f}")

# 输出所有组合按分数排序
print("\nTop 5 combinations:")
all_combo_data = []
for combo in all_combinations:
    perf_delta = 0
    budget_delta = 0
    schedule_delta = 0
    risk_delta = 0
    
    for decision_id in combo:
        perf_delta += decision_data[decision_id]['delta']['performance_multiplier']
        budget_delta += decision_data[decision_id]['delta']['budget_overrun_pct']
        schedule_delta += decision_data[decision_id]['delta']['schedule_delay_months']
        risk_delta += decision_data[decision_id]['delta']['risk_points']
    
    perf = baseline['performance_multiplier'] + perf_delta
    budget = baseline['budget_overrun_pct'] + budget_delta
    schedule = baseline['schedule_delay_months'] + schedule_delta
    risk = baseline['risk_points'] + risk_delta
    
    score = calculate_score(perf, budget, schedule, risk)
    
    all_combo_data.append({
        'decision_ids': sorted(combo),
        'score': score
    })

# 按分数排序
sorted_combos = sorted(all_combo_data, key=lambda x: x['score'], reverse=True)
for i, combo in enumerate(sorted_combos[:5]):
    print(f"{i+1}. {combo['decision_ids']}: score={combo['score']:.2f}")