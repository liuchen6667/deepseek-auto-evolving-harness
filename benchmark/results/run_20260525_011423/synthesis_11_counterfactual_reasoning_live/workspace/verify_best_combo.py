from itertools import combinations
import json

# Load decisions data
with open('decision_delta_matrix.json', 'r') as f:
    decisions_data = json.load(f)

baseline = {
    'performance_multiplier': 1.2,
    'budget_overrun_pct': 200,
    'schedule_delay_months': 6,
    'risk_points': 9
}

def calculate_score(outcome):
    return (outcome['performance_multiplier'] * 10 
            - outcome['budget_overrun_pct'] / 10 
            - outcome['schedule_delay_months'] * 5 
            - outcome['risk_points'] * 3)

baseline_score = calculate_score(baseline)
print(f'Baseline score: {baseline_score}')

# Generate all combinations of 3 decisions
all_combos = list(combinations(decisions_data, 3))
print(f'Total combinations: {len(all_combos)}')

best_score = -float('inf')
best_combo = None
best_combo_ids = None

for combo in all_combos:
    # Apply all deltas
    outcome = {k: baseline[k] for k in baseline}
    for decision in combo:
        for key in outcome:
            outcome[key] += decision['delta'][key]
    
    score = calculate_score(outcome)
    current_ids = sorted([d['decision_id'] for d in combo])
    
    if score > best_score:
        best_score = score
        best_combo = combo
        best_combo_ids = current_ids
    elif score == best_score:
        # Tie-break: alphabetically smallest sorted decision_ids
        if current_ids < best_combo_ids:
            best_score = score
            best_combo = combo
            best_combo_ids = current_ids

print(f'\nBest score: {best_score}')
print(f'Best combo IDs: {best_combo_ids}')
print(f'Best combo:')
for decision in best_combo:
    print(f"  - {decision['decision_id']}: {decision['alternative']}")

# Calculate the outcome for the best combo
outcome = {k: baseline[k] for k in baseline}
for decision in best_combo:
    for key in outcome:
        outcome[key] += decision['delta'][key]

print(f'\nCombined outcome:')
for key, value in outcome.items():
    print(f'  {key}: {value}')
print(f'Score: {calculate_score(outcome)}')
