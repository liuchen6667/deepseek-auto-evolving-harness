import csv
import json

# 读取 CSV 文件并计算每个 category 的 amount 总和
category_sums = {}

with open('data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row['category']
        amount = int(row['amount'])
        
        if category in category_sums:
            category_sums[category] += amount
        else:
            category_sums[category] = amount

# 将结果写入 JSON 文件
with open('result.json', 'w') as f:
    json.dump(category_sums, f, indent=2)

print("Done:", category_sums)