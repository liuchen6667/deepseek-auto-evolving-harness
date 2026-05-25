import json
import itertools

# 读取基线数据
with open('baseline_outcome.json') as f:
    baseline = json.load(f)

# 读取决策矩阵
with open('decision_delta_matrix.json') as f:
    decisions = json.load(f)

# 读取计分策略
with open('scoring_policy.yaml') as f:
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

print('权重:', weights)
print('\n基线值:', baseline)

# 计算基线分数
def calculate_score(pm, bo, sd, rp):
    return (pm * weights['performance_multiplier_weight']) - \
           (bo / weights['budget_overrun_divisor']) - \
           (sd * weights['schedule_delay_month_weight']) - \
           (rp * weights['risk_point_weight'])

baseline_score = calculate_score(baseline['performance_multiplier'], 
                                 baseline['budget_overrun_pct'], 
                                 baseline['schedule_delay_months'], 
                                 baseline['risk_points'])
print('基线分数:', baseline_score)

# 计算每个单独决策的分数改进
individual_results = []
for decision in decisions:
    # 应用增量
    new_pm = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
    new_bo = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
    new_sd = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
    new_rp = baseline['risk_points'] + decision['delta']['risk_points']
    
    new_score = calculate_score(new_pm, new_bo, new_sd, new_rp)
    score_improvement = new_score - baseline_score
    
    individual_results.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': new_score,
        'score_improvement': score_improvement
    })

print('\n单独决策结果:')
for res in individual_results:
    print(res['decision_id'] + ': 改进 ' + str(res['score_improvement']))

# 排序并取前三
individual_results.sort(key=lambda x: x['score_improvement'], reverse=True)
top_three = individual_results[:3]
print('\n前三名:')
for res in top_three:
    print(res['decision_id'] + ': 改进 ' + str(res['score_improvement']))