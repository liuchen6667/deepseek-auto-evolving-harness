import csv
from collections import defaultdict
import json
import os

# 读取数据
totals = defaultdict(float)

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product = row['product']
        amount = float(row['amount'])
        totals[product] += amount

# 按总销售额降序排序
sorted_totals = dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))

# 确保输出目录存在
os.makedirs('output', exist_ok=True)

# 写入 JSON 文件
with open('output/result.json', 'w') as f:
    json.dump(sorted_totals, f, indent=2)

print("分析完成，结果已保存到 output/result.json")
print("各产品总销售额:")
for product, total in sorted_totals.items():
    print(f"  {product}: {total}")