import json
import yaml

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

# 计算基准分数
pm_base = baseline['performance_multiplier']
bo_base = baseline['budget_overrun_pct']
sd_base = baseline['schedule_delay_months']
rp_base = baseline['risk_points']

baseline_score = (pm_base * w_pm) - (bo_base / d_bo) - (sd_base * w_sd) - (rp_base * w_rp)
print(f"Baseline score: {baseline_score}")

# 计算每个决策的分数改进
results = []
for decision in decisions:
    decision_id = decision['decision_id']
    alternative = decision['alternative']
    delta = decision['delta']
    
    # 计算新指标
    new_pm = pm_base + delta['performance_multiplier']
    new_bo = bo_base + delta['budget_overrun_pct']
    new_sd = sd_base + delta['schedule_delay_months']
    new_rp = rp_base + delta['risk_points']
    
    # 计算新分数
    new_score = (new_pm * w_pm) - (new_bo / d_bo) - (new_sd * w_sd) - (new_rp * w_rp)
    score_improvement = new_score - baseline_score
    
    results.append({
        'decision_id': decision_id,
        'alternative': alternative,
        'projected_score': new_score,
        'score_improvement': score_improvement
    })
    
    print(f"{decision_id}: {alternative} - Score: {new_score:.2f}, Improvement: {score_improvement:.2f}")

# 按改进分数排序
sorted_results = sorted(results, key=lambda x: x['score_improvement'], reverse=True)
print("\nTop 3 improvements:")
for i, result in enumerate(sorted_results[:3]):
    print(f"{i+1}. {result['decision_id']}: {result['score_improvement']:.2f}")

# 输出用于检查
print(f"\nTotal decisions: {len(results)}")