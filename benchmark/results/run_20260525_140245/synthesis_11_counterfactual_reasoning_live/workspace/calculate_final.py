import json
import itertools

# Load data
with open('baseline_outcome.json', 'r') as f:
    baseline = json.load(f)

with open('decision_delta_matrix.json', 'r') as f:
    decisions = json.load(f)

# Parse YAML weights
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
    score_improvement = projected_score - baseline_score  # Negative means improvement
    
    individual_scores.append({
        'decision_id': decision['decision_id'],
        'alternative': decision['alternative'],
        'projected_score': round(projected_score, 2),
        'score_improvement': round(score_improvement, 2)
    })

# Sort by score_improvement descending (most negative first)
individual_scores.sort(key=lambda x: x['score_improvement'], reverse=True)

# Get top 3
individual_rank = individual_scores[:3]
print('Top 3 individual improvements (most negative first):')
for item in individual_rank:
    print(f"  {item['decision_id']}: improvement={item['score_improvement']}")

# Find all combinations of exactly 3 decisions
decision_ids = [d['decision_id'] for d in decisions]
combinations = list(itertools.combinations(decision_ids, 3))

# Calculate best combination (lowest score)
best_score = float('inf')
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
    
    if projected_score < best_score:
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

print(f'\nBest combination (sorted): {sorted(best_combination)}')
print(f'Best projected score: {best_score}')
print(f'Best projection: {best_projection}')

# Load recommendations
with open('recommendation_catalog.json', 'r') as f:
    rec_catalog = json.load(f)

# Select 2 recommendations alphabetically
recommendations = sorted(rec_catalog['recommendation_codes'])[:2]
print(f'\nRecommendations: {recommendations}')

# Prepare final output
output = {
    "individual_rank": individual_rank,
    "best_three_change_plan": sorted(best_combination),  # Alphabetical order
    "combined_projection": {
        "performance_multiplier": round(best_projection['performance_multiplier'], 2),
        "budget_overrun_pct": int(best_projection['budget_overrun_pct']),
        "schedule_delay_months": int(best_projection['schedule_delay_months']),
        "risk_points": int(best_projection['risk_points']),
        "score": round(best_score, 2)
    },
    "recommendations": recommendations
}

print('\nFinal output prepared.')