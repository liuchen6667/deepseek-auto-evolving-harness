import json

# Baseline outcome
baseline = {
    'performance_multiplier': 1.2,
    'budget_overrun_pct': 200,
    'schedule_delay_months': 6,
    'risk_points': 9
}

# Weights from scoring policy
weights = {
    'performance_multiplier_weight': 10,
    'budget_overrun_divisor': 10,
    'schedule_delay_month_weight': 5,
    'risk_point_weight': 3
}

def calculate_score(outcome):
    return (outcome['performance_multiplier'] * weights['performance_multiplier_weight'] 
            - outcome['budget_overrun_pct'] / weights['budget_overrun_divisor'] 
            - outcome['schedule_delay_months'] * weights['schedule_delay_month_weight'] 
            - outcome['risk_points'] * weights['risk_point_weight'])

baseline_score = calculate_score(baseline)
print(f'Baseline score: {baseline_score}')

# Individual decision deltas (from decision_delta_matrix.json)
deltas = {
    'stack': {'performance_multiplier': 0.6, 'budget_overrun_pct': -80, 'schedule_delay_months': -2, 'risk_points': -2},
    'testing': {'performance_multiplier': 0.4, 'budget_overrun_pct': -30, 'schedule_delay_months': -2, 'risk_points': -2},
    'delivery': {'performance_multiplier': 0.2, 'budget_overrun_pct': -40, 'schedule_delay_months': -1, 'risk_points': -2}
}

print('\nIndividual scores:')
for name, delta in deltas.items():
    projected = {k: baseline[k] + delta[k] for k in baseline}
    score = calculate_score(projected)
    improvement = score - baseline_score
    print(f'{name}: score={score}, improvement={improvement}')

# Combined projection
print('\nCombined projection (stack + delivery + testing):')
combined_delta = {
    'performance_multiplier': 0.6 + 0.2 + 0.4,
    'budget_overrun_pct': -80 + (-40) + (-30),
    'schedule_delay_months': -2 + (-1) + (-2),
    'risk_points': -2 + (-2) + (-2)
}

combined_outcome = {k: baseline[k] + combined_delta[k] for k in baseline}
combined_score = calculate_score(combined_outcome)
print(f'Outcome: {combined_outcome}')
print(f'Score: {combined_score}')
print(f'Improvement: {combined_score - baseline_score}')
