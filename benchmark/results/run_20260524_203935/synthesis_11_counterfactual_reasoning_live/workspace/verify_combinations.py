import json
import yaml
import itertools

# Load data
with open('baseline_outcome.json') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json') as f:
    decisions = json.load(f)

with open('scoring_policy.yaml') as f:
    policy = yaml.safe_load(f)

# Score formula
performance_weight = policy['score_formula']['performance_multiplier_weight']
budget_divisor = policy['score_formula']['budget_overrun_divisor']
schedule_weight = policy['score_formula']['schedule_delay_month_weight']
risk_weight = policy['score_formula']['risk_point_weight']

def calculate_score(pm, bo, sd, rp):
    return pm * performance_weight - bo / budget_divisor - sd * schedule_weight - rp * risk_weight

# Create a dict for quick delta lookup
delta_dict = {d['decision_id']: d['delta'] for d in decisions}
decision_ids = list(delta_dict.keys())

# Find all combinations with best score
best_score = -float('inf')
best_combinations = []

for combo in itertools.combinations(decision_ids, 3):
    # Apply linear addition of deltas
    pm_delta = 0
    bo_delta = 0
    sd_delta = 0
    rp_delta = 0
    
    for decision_id in combo:
        delta = delta_dict[decision_id]
        pm_delta += delta['performance_multiplier']
        bo_delta += delta['budget_overrun_pct']
        sd_delta += delta['schedule_delay_months']
        rp_delta += delta['risk_points']
    
    # Calculate new metrics
    pm = baseline['performance_multiplier'] + pm_delta
    bo = baseline['budget_overrun_pct'] + bo_delta
    sd = baseline['schedule_delay_months'] + sd_delta
    rp = baseline['risk_points'] + rp_delta
    
    projected_score = calculate_score(pm, bo, sd, rp)
    
    if projected_score > best_score:
        best_score = projected_score
        best_combinations = [(sorted(combo), projected_score)]
    elif abs(projected_score - best_score) < 1e-10:  # Float comparison
        best_combinations.append((sorted(combo), projected_score))

print(f"Best score: {best_score}")
print(f"Number of combinations with best score: {len(best_combinations)}")
print("\nAll best combinations:")
for combo, score in best_combinations:
    print(f"  {combo}: {score}")

# Apply tie-break: alphabetically smallest sorted decision_ids
best_combinations.sort(key=lambda x: ''.join(x[0]))
print(f"\nAfter tie-break (alphabetical): {best_combinations[0][0]}")

# Check if our selected combination is correct
selected = ['delivery', 'stack', 'testing']
selected_sorted = sorted(selected)
print(f"\nOur selection: {selected_sorted}")
print(f"Matches best after tie-break: {selected_sorted == best_combinations[0][0]}")
