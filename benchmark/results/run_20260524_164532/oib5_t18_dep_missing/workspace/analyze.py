import csv
import json

# 读取 CSV 文件
category_totals = {}

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row['category']
        amount = float(row['amount'])  # 转换为数值类型
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

# 将结果写入 JSON 文件
with open('result.json', 'w') as f:
    json.dump(category_totals, f, indent=2)

print("Done:", category_totals)