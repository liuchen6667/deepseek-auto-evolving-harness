import csv
import json

result = {}
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row['category']
        amount = float(row['amount'])
        result[category] = result.get(category, 0) + amount

with open('result.json', 'w') as f:
    json.dump(result, f, indent=2)

print('Done:', result)
