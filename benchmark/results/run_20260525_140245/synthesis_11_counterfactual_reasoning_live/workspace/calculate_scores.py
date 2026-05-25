import json
import itertools

# Load data
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

with open('scoring_policy.yaml', 'r') as f:
    yaml_content = f.read()

# Parse YAML (simplified)
weights = {
    'performance_multiplier_weight': 10,
    'budget_overrun_divisor': 10,
    'schedule_delay_month_weight': 5,
    'risk_point_weight': 3
}

# Calculate baseline score
def calculate_score(params):
    return (params['performance_multiplier'] * weights['performance_multiplier_weight'] +
            params['budget_overrun_pct'] / weights['budget_overrun_divisor'] +
            params['schedule_delay_months'] * weights['schedule_delay_month_weight'] +
            params['risk_points'] * weights['risk_point_weight'])

baseline_score = calculate_score(baseline)
print(f'Baseline score: {baseline_score}')

# Calculate individual scores
individual_scores = []
for decision in decisions:
    # Apply delta to baseline
    projected = {
        'performance_multiplier': baseline['performance_multiplier'] + decision['delta']['performance_multiplier'],
        'budget_overrun_pct': baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct'],
        'schedule_delay_months': baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months'],
        'risk_points': baseline['risk_points'] + decision['delta']['risk_points']
    }
    
    projected_score = calculate_score(projected)
    score_improvement = projected_score - baseline_score
    
    individual_scores.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': round(projected_score, 2),
        'score_improvement': round(score_improvement, 2)
    })

# Sort by score_improvement descending
individual_scores.sort(key=lambda x: x['score_improvement'], reverse=True)
print('\nTop 3 individual improvements:')
for i, item in enumerate(individual_scores[:3]):
    print(f"{i+1}. {item['decision_id']}: {item['score_improvement']}")

# Find all combinations of exactly 3 decisions
decision_ids = [d['decision_id'] for d in decisions]
combinations = list(itertools.combinations(decision_ids, 3))
print(f'\nTotal combinations of 3 decisions: {len(combinations)}')

# Calculate best combination
best_score = float('-inf')
best_combination = None
best_projection = None

for combo in combinations:
    # Sum all deltas for this combination
    total_delta = {
        'performance_multiplier': 0.0,
        'budget_overrun_pct': 0,
        'schedule_delay_months': 0,
        'risk_points': 0
    }
    
    for decision in decisions:
        if decision['decision_id'] in combo:
            for key in total_delta:
                if key in decision['delta']:
                    total_delta[key] += decision['delta'][key]
    
    # Apply to baseline
    projected = {
        'performance_multiplier': baseline['performance_multiplier'] + total_delta['performance_multiplier'],
        'budget_overrun_pct': baseline['budget_overrun_pct'] + total_delta['budget_overrun_pct'],
        'schedule_delay_months': baseline['schedule_delay_months'] + total_delta['schedule_delay_months'],
        'risk_points': baseline['risk_points'] + total_delta['risk_points']
    }
    
    projected_score = calculate_score(projected)
    
    if projected_score > best_score:
        best_score = projected_score
        best_combination = combo
        best_projection = projected
    elif projected_score == best_score:
        # Tie-break: alphabetically smallest sorted decision ids
        current_sorted = sorted(combo)
        best_sorted = sorted(best_combination)
        if current_sorted < best_sorted:
            best_score = projected_score
            best_combination = combo
            best_projection = projected

print(f'\nBest combination: {best_combination}')
print(f'Best projected score: {best_score}')
print(f'Best projection: {best_projection}')

# Load recommendations
with open('recommendation_catalog.json', 'r') as f:
    rec_catalog = json.load(f)

print(f'\nAvailable recommendations: {rec_catalog["recommendation_codes"]}')
print(f'Sorted: {sorted(rec_catalog["recommendation_codes"])[:2]}')