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

with open('recommendation_catalog.json') as f:
    catalog = json.load(f)

# Score formula
performance_weight = policy['score_formula']['performance_multiplier_weight']
budget_divisor = policy['score_formula']['budget_overrun_divisor']
schedule_weight = policy['score_formula']['schedule_delay_month_weight']
risk_weight = policy['score_formula']['risk_point_weight']

def calculate_score(pm, bo, sd, rp):
    return pm * performance_weight - bo / budget_divisor - sd * schedule_weight - rp * risk_weight

# Baseline score
baseline_score = calculate_score(
    baseline['performance_multiplier'],
    baseline['budget_overrun_pct'],
    baseline['schedule_delay_months'],
    baseline['risk_points']
)
print(f"Baseline score: {baseline_score}")

# Individual decision analysis
individual_results = []
for decision in decisions:
    # Apply delta to baseline
    pm = baseline['performance_multiplier'] + decision['delta']['performance_multiplier']
    bo = baseline['budget_overrun_pct'] + decision['delta']['budget_overrun_pct']
    sd = baseline['schedule_delay_months'] + decision['delta']['schedule_delay_months']
    rp = baseline['risk_points'] + decision['delta']['risk_points']
    
    projected_score = calculate_score(pm, bo, sd, rp)
    score_improvement = projected_score - baseline_score
    
    individual_results.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': round(projected_score, 2),
        'score_improvement': round(score_improvement, 2)
    })

# Sort by score_improvement descending
individual_results.sort(key=lambda x: x['score_improvement'], reverse=True)
print("\nTop 3 individual decisions:")
for i, res in enumerate(individual_results[:3]):
    print(f"{i+1}. {res['decision_id']}: {res['score_improvement']}")

# Find best combination of exactly 3 decisions
decision_ids = [d['decision_id'] for d in decisions]
best_combination = None
best_score = -float('inf')
best_metrics = None

# Create a dict for quick delta lookup
delta_dict = {d['decision_id']: d['delta'] for d in decisions}

# Generate all combinations of 3 decisions
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
        best_combination = sorted(combo)  # Sort for tie-breaking
        best_metrics = {
            'performance_multiplier': round(pm, 2),
            'budget_overrun_pct': round(bo, 2),
            'schedule_delay_months': round(sd, 2),
            'risk_points': round(rp, 2),
            'score': round(projected_score, 2)
        }
    elif projected_score == best_score:
        # Tie-break: alphabetically smallest sorted decision_ids
        sorted_combo = sorted(combo)
        if ''.join(sorted_combo) < ''.join(best_combination):
            best_combination = sorted_combo
            best_metrics = {
                'performance_multiplier': round(pm, 2),
                'budget_overrun_pct': round(bo, 2),
                'schedule_delay_months': round(sd, 2),
                'risk_points': round(rp, 2),
                'score': round(projected_score, 2)
            }

print(f"\nBest 3-decision combination: {best_combination}")
print(f"Combined score: {best_score}")
print(f"Combined metrics: {best_metrics}")

# Select recommendations (exactly 2, alphabetical)
recommendations = sorted(catalog['recommendation_codes'])[:2]
print(f"\nRecommendations: {recommendations}")

# Prepare final output
output = {
    "individual_rank": individual_results[:3],
    "best_three_change_plan": best_combination,
    "combined_projection": best_metrics,
    "recommendations": recommendations
}

# Save to file
with open('counterfactual_analysis.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nOutput saved to counterfactual_analysis.json")
