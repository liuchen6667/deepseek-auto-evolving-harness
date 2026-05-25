import json
import yaml
import math

# Load baseline outcome
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

# Load decision delta matrix
with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

# Load scoring policy
with open('scoring_policy.yaml', 'r') as f:
    policy = yaml.safe_load(f)

weights = policy['score_formula']

# Calculate baseline score
def calculate_score(outcome):
    return (outcome['performance_multiplier'] * weights['performance_multiplier_weight'] 
            - outcome['budget_overrun_pct'] / weights['budget_overrun_divisor'] 
            - outcome['schedule_delay_months'] * weights['schedule_delay_month_weight'] 
            - outcome['risk_points'] * weights['risk_point_weight'])

baseline_score = calculate_score(baseline)
print(f'Baseline score: {baseline_score}')

# Calculate scores for each alternative
individual_results = []
for decision in decisions:
    # Apply delta to baseline
    projected_outcome = {
        'performance_multiplier': baseline['performance_multiplier'] + decision['delta']['performance_multiplier'],
        'budget_overrun_pct': baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct'],
        'schedule_delay_months': baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months'],
        'risk_points': baseline['risk_points'] + decision['delta']['risk_points']
    }
    
    projected_score = calculate_score(projected_outcome)
    score_improvement = projected_score - baseline_score
    
    individual_results.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': projected_score,
        'score_improvement': score_improvement,
        'projected_outcome': projected_outcome
    })

# Sort by score_improvement descending
individual_results.sort(key=lambda x: x['score_improvement'], reverse=True)

print('\nIndividual results (top 3):')
for i, result in enumerate(individual_results[:3]):
    print(f"{i+1}. {result['decision_id']}: {result['alternative']}, improvement: {result['score_improvement']:.2f}")

# Now find best combination of exactly 3 decisions
from itertools import combinations

best_combination = None
best_score = -float('inf')
best_outcome = None

# Generate all combinations of 3 decisions
all_combinations = list(combinations(decisions, 3))
print(f'\nTotal combinations to evaluate: {len(all_combinations)}')

for combo in all_combinations:
    # Apply all deltas (linear addition)
    projected_outcome = {
        'performance_multiplier': baseline['performance_multiplier'],
        'budget_overrun_pct': baseline['budget_overrun_pct'],
        'schedule_delay_months': baseline['schedule_delay_months'],
        'risk_points': baseline['risk_points']
    }
    
    for decision in combo:
        projected_outcome['performance_multiplier'] += decision['delta']['performance_multiplier']
        projected_outcome['budget_overrun_pct'] += decision['delta']['budget_overrun_pct']
        projected_outcome['schedule_delay_months'] += decision['delta']['schedule_delay_months']
        projected_outcome['risk_points'] += decision['delta']['risk_points']
    
    projected_score = calculate_score(projected_outcome)
    
    if projected_score > best_score:
        best_score = projected_score
        best_combination = combo
        best_outcome = projected_outcome
    elif projected_score == best_score:
        # Tie-break: alphabetically smallest sorted decision_ids
        current_ids = sorted([d['decision_id'] for d in combo])
        best_ids = sorted([d['decision_id'] for d in best_combination])
        
        # Compare lexicographically
        if current_ids < best_ids:
            best_score = projected_score
            best_combination = combo
            best_outcome = projected_outcome

print(f'\nBest combination:')
for decision in best_combination:
    print(f"  - {decision['decision_id']}: {decision['alternative']}")
print(f'Best score: {best_score:.2f}')
print(f'Best outcome: {best_outcome}')
print(f'Score improvement: {best_score - baseline_score:.2f}')

# Get recommendation codes
with open('recommendation_catalog.json', 'r') as f:
    catalog = json.load(f)

recommendation_codes = catalog['recommendation_codes']
print(f'\nAvailable recommendation codes: {recommendation_codes}')
