import json

# 读取基线值
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

# 读取决策矩阵
with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

# 读取评分策略
with open('scoring_policy.yaml', 'r') as f:
    lines = f.readlines()
    weights = {}
    for line in lines:
        if 'performance_multiplier_weight' in line:
            weights['performance_multiplier_weight'] = int(line.split(':')[1].strip())
        elif 'budget_overrun_divisor' in line:
            weights['budget_overrun_divisor'] = int(line.split(':')[1].strip())
        elif 'schedule_delay_month_weight' in line:
            weights['schedule_delay_month_weight'] = int(line.split(':')[1].strip())
        elif 'risk_point_weight' in line:
            weights['risk_point_weight'] = int(line.split(':')[1].strip())

# 计算基线分数
def calculate_score(pm, bo, sd, rp):
    return (pm * weights['performance_multiplier_weight'] +
            bo / weights['budget_overrun_divisor'] +
            sd * weights['schedule_delay_month_weight'] +
            rp * weights['risk_point_weight'])

baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)
print(f'Baseline score: {baseline_score}')

# 计算每个决策的分数改进
results = []
for decision in decisions:
    # 应用 delta
    new_pm = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
    new_bo = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
    new_sd = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
    new_rp = baseline['risk_points'] + decision['delta']['risk_points']
    
    # 计算新分数
    new_score = calculate_score(new_pm, new_bo, new_sd, new_rp)
    
    # 计算改进
    improvement = new_score - baseline_score
    
    results.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': round(new_score, 2),
        'score_improvement': round(improvement, 2)
    })

# 按改进降序排序
results.sort(key=lambda x: x['score_improvement'], reverse=True)

print('\nTop 3 individual improvements:')
for i, r in enumerate(results[:3]):
    print(f"{i+1}. {r['decision_id']}: {r['score_improvement']}")

# 输出前3名
print('\nTop 3 for individual_rank:')
for r in results[:3]:
    print(json.dumps(r, indent=2))

# 现在找出最好的3个决策组合
# 我们需要选择恰好3个决策，计算线性叠加的delta
from itertools import combinations

# 所有决策ID
all_decision_ids = [d['decision_id'] for d in decisions]
best_combination = None
best_score = float('-inf')
best_combination_ids = None

for combo in combinations(all_decision_ids, 3):
    # 计算组合delta
    delta_pm = 0
    delta_bo = 0
    delta_sd = 0
    delta_rp = 0
    
    for decision_id in combo:
        decision = next(d for d in decisions if d['decision_id'] == decision_id)
        delta_pm += decision['delta']['performance_multiplier']
        delta_bo += decision['delta']['budget_overrun_pct']
        delta_sd += decision['delta']['schedule_delay_months']
        delta_rp += decision['delta']['risk_points']
    
    # 计算新值
    new_pm = baseline['performance_multiplier'] + delta_pm
    new_bo = baseline['budget_overrun_pct'] + delta_bo
    new_sd = baseline['schedule_delay_months'] + delta_sd
    new_rp = baseline['risk_points'] + delta_rp
    
    # 计算分数
    new_score = calculate_score(new_pm, new_bo, new_sd, new_rp)
    
    if new_score > best_score:
        best_score = new_score
        best_combination = (new_pm, new_bo, new_sd, new_rp, new_score)
        best_combination_ids = sorted(combo)  # 按字母序排序
    elif new_score == best_score:
        # 并列情况，按字母序选择最小的决策ID组合
        sorted_combo = sorted(combo)
        if best_combination_ids is None or sorted_combo < best_combination_ids:
            best_combination_ids = sorted_combo
            best_combination = (new_pm, new_bo, new_sd, new_rp, new_score)

print(f'\nBest combination: {best_combination_ids}')
print(f'Best score: {best_score}')
print(f'Improvement: {best_score - baseline_score}')
print(f'\nCombined projection:')
print(f'performance_multiplier: {best_combination[0]:.2f}')
print(f'budget_overrun_pct: {best_combination[1]:.2f}')
print(f'schedule_delay_months: {best_combination[2]:.2f}')
print(f'risk_points: {best_combination[3]:.2f}')
print(f'score: {best_combination[4]:.2f}')

# 读取推荐目录
with open('recommendation_catalog.json', 'r') as f:
    catalog = json.load(f)

print(f'\nAll recommendation codes: {catalog["recommendation_codes"]}')
print(f'Sorted: {sorted(catalog["recommendation_codes"])}')