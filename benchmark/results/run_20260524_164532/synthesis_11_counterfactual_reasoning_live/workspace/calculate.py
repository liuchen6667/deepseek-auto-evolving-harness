import json
import yaml
import itertools

# 加载数据
baseline = json.load(open('baseline_outcome.json'))
decisions = json.load(open('decision_delta_matrix.json'))
policy = yaml.safe_load(open('scoring_policy.yaml'))
recommendations = json.load(open('recommendation_catalog.json'))

# 提取计分公式
formula = policy['score_formula']
performance_weight = formula['performance_multiplier_weight']
budget_divisor = formula['budget_overrun_divisor']
schedule_weight = formula['schedule_delay_month_weight']
risk_weight = formula['risk_point_weight']

# 计算得分函数
def calculate_score(outcome):
    # 得分 = performance_multiplier * weight - budget_overrun/divisor - schedule_delay * weight - risk_points * weight
    score = (outcome['performance_multiplier'] * performance_weight) - \
            (outcome['budget_overrun_pct'] / budget_divisor) - \
            (outcome['schedule_delay_months'] * schedule_weight) - \
            (outcome['risk_points'] * risk_weight)
    return score

# 计算基线得分
baseline_score = calculate_score(baseline)
print(f"Baseline score: {baseline_score}")
print(f"Baseline outcome: {baseline}")

# 计算每个单独决策的改进
individual_results = []
for decision in decisions:
    # 应用delta到基线
    projected = baseline.copy()
    delta = decision['delta']
    for key in projected:
        if key in delta:
            projected[key] += delta[key]
    
    # 计算得分
    projected_score = calculate_score(projected)
    score_improvement = projected_score - baseline_score
    
    individual_results.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': round(projected_score, 2),
        'score_improvement': round(score_improvement, 2)
    })

# 按改进排序
individual_results.sort(key=lambda x: x['score_improvement'], reverse=True)
print("\nIndividual improvements (top 3):")
for i, res in enumerate(individual_results[:3]):
    print(f"  {i+1}. {res['decision_id']}: {res['score_improvement']}")

# 生成所有可能的3个决策组合
decision_ids = [d['decision_id'] for d in decisions]
combinations = list(itertools.combinations(decision_ids, 3))
print(f"\nTotal combinations of 3 decisions: {len(combinations)}")

# 为每个决策创建delta映射
delta_map = {d['decision_id']: d['delta'] for d in decisions}

# 评估每个组合
best_combination = None
best_score = -float('inf')
tie_candidates = []

for combo in combinations:
    # 应用所有deltas
    projected = baseline.copy()
    for decision_id in combo:
        delta = delta_map[decision_id]
        for key in projected:
            if key in delta:
                projected[key] += delta[key]
    
    projected_score = calculate_score(projected)
    score_improvement = projected_score - baseline_score
    
    # 跟踪最佳组合
    if score_improvement > best_score:
        best_score = score_improvement
        best_combination = combo
        tie_candidates = [combo]
    elif score_improvement == best_score:
        tie_candidates.append(combo)

print(f"\nBest score improvement: {best_score}")
print(f"Best combination: {best_combination}")

# 处理平局
if len(tie_candidates) > 1:
    print(f"Found {len(tie_candidates)} combinations with same score")
    # 按字母顺序排序决策ID
    sorted_candidates = [sorted(combo) for combo in tie_candidates]
    # 按字母顺序选择最小的
    sorted_candidates.sort()
    best_sorted = sorted_candidates[0]
    # 找到原始组合
    for combo in tie_candidates:
        if sorted(combo) == best_sorted:
            best_combination = combo
            break
    print(f"Selected after tie-break: {best_combination}")

# 计算最佳组合的投影结果
projected_best = baseline.copy()
for decision_id in best_combination:
    delta = delta_map[decision_id]
    for key in projected_best:
        if key in delta:
            projected_best[key] += delta[key]

best_score_total = calculate_score(projected_best)
print(f"\nBest projected outcome: {projected_best}")
print(f"Best total score: {best_score_total}")

# 准备输出
output = {
    'individual_rank': individual_results[:3],
    'best_three_change_plan': sorted(best_combination),  # 按字母序
    'combined_projection': {
        'performance_multiplier': round(projected_best['performance_multiplier'], 2),
        'budget_overrun_pct': round(projected_best['budget_overrun_pct']),
        'schedule_delay_months': round(projected_best['schedule_delay_months']),
        'risk_points': round(projected_best['risk_points']),
        'score': round(best_score_total, 2)
    },
    'recommendations': sorted(recommendations['recommendation_codes'])[:2]  # 按字母序取前2
}

# 写入文件
with open('counterfactual_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput written to counterfactual_analysis.json")
print(json.dumps(output, indent=2))