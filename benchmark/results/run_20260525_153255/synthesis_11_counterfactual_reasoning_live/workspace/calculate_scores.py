import json
import yaml
import itertools

# 读取数据
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

with open('scoring_policy.yaml', 'r') as f:
    policy = yaml.safe_load(f)

with open('recommendation_catalog.json', 'r') as f:
    recommendations = json.load(f)

# 提取权重
weight_perf = policy['score_formula']['performance_multiplier_weight']
divisor_budget = policy['score_formula']['budget_overrun_divisor']
weight_schedule = policy['score_formula']['schedule_delay_month_weight']
weight_risk = policy['score_formula']['risk_point_weight']

# 计算基线得分
def calculate_score(pm, bo, sd, rp):
    return pm * weight_perf - (bo / divisor_budget) - sd * weight_schedule - rp * weight_risk

baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)
print(f'Baseline score: {baseline_score}')

# 计算每个决策的 projected_score 和 improvement
results = []
for d in decisions:
    delta = d['delta']
    projected_pm = baseline['performance_multiplier'] + delta['performance_multiplier']
    projected_bo = baseline['budget_overrun_pct'] + delta['budget_overrun_pct']
    projected_sd = baseline['schedule_delay_months'] + delta['schedule_delay_months']
    projected_rp = baseline['risk_points'] + delta['risk_points']
    
    projected_score = calculate_score(projected_pm, projected_bo, projected_sd, projected_rp)
    improvement = projected_score - baseline_score
    
    results.append({
        'decision_id': d['decision_id'],
        'alternative': d['alternative'],
        'projected_score': round(projected_score, 2),
        'score_improvement': round(improvement, 2)
    })

# 按 improvement 排序
sorted_results = sorted(results, key=lambda x: x['score_improvement'], reverse=True)
print('\nIndividual results (sorted by improvement):')
for r in sorted_results:
    print(f"{r['decision_id']}: {r['score_improvement']}")

# 只取前三名
individual_rank = sorted_results[:3]
print('\nTop 3:')
for r in individual_rank:
    print(f"{r['decision_id']}: {r['score_improvement']}")

# 找出所有 3 个决策的组合
all_decision_ids = [d['decision_id'] for d in decisions]
combinations = list(itertools.combinations(all_decision_ids, 3))
print(f'\nTotal combinations of 3: {len(combinations)}')

# 计算每个组合的总 improvement 和 projected 值
best_score = float('-inf')
best_combination = None
best_projection = None

for combo in combinations:
    total_delta_pm = 0
    total_delta_bo = 0
    total_delta_sd = 0
    total_delta_rp = 0
    
    for decision_id in combo:
        for d in decisions:
            if d['decision_id'] == decision_id:
                delta = d['delta']
                total_delta_pm += delta['performance_multiplier']
                total_delta_bo += delta['budget_overrun_pct']
                total_delta_sd += delta['schedule_delay_months']
                total_delta_rp += delta['risk_points']
                break
    
    projected_pm = baseline['performance_multiplier'] + total_delta_pm
    projected_bo = baseline['budget_overrun_pct'] + total_delta_bo
    projected_sd = baseline['schedule_delay_months'] + total_delta_sd
    projected_rp = baseline['risk_points'] + total_delta_rp
    
    projected_score = calculate_score(projected_pm, projected_bo, projected_sd, projected_rp)
    
    if projected_score > best_score:
        best_score = projected_score
        best_combination = combo
        best_projection = {
            'performance_multiplier': projected_pm,
            'budget_overrun_pct': projected_bo,
            'schedule_delay_months': projected_sd,
            'risk_points': projected_rp,
            'score': projected_score
        }
    elif projected_score == best_score:
        # 按字母序排序，选择字母序最小的组合
        sorted_combo = sorted(combo)
        sorted_best = sorted(best_combination)
        if sorted_combo < sorted_best:
            best_combination = combo
            best_projection = {
                'performance_multiplier': projected_pm,
                'budget_overrun_pct': projected_bo,
                'schedule_delay_months': projected_sd,
                'risk_points': projected_rp,
                'score': projected_score
            }

print(f'\nBest combination: {best_combination}')
print(f'Best projection: {best_projection}')
print(f'Best score: {best_score}')

# 按字母序排序 best_three_change_plan
best_three_sorted = sorted(best_combination)
print(f'\nBest three (sorted): {best_three_sorted}')

# 选择 recommendations
recommendation_codes = recommendations['recommendation_codes']
recommendation_codes.sort()  # 按字母序排序
selected_recommendations = recommendation_codes[:2]  # 正好 2 条
print(f'\nSelected recommendations: {selected_recommendations}')

# 输出最终 JSON
output = {
    'individual_rank': individual_rank,
    'best_three_change_plan': best_three_sorted,
    'combined_projection': {
        'performance_multiplier': round(best_projection['performance_multiplier'], 2),
        'budget_overrun_pct': round(best_projection['budget_overrun_pct'], 2),
        'schedule_delay_months': round(best_projection['schedule_delay_months'], 2),
        'risk_points': round(best_projection['risk_points'], 2),
        'score': round(best_projection['score'], 2)
    },
    'recommendations': selected_recommendations
}

print('\nOutput JSON:')
print(json.dumps(output, indent=2))

# 写入文件
with open('counterfactual_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)