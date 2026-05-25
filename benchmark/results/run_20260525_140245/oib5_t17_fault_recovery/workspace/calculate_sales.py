import csv
import json
from collections import defaultdict

# 读取 CSV 文件
sales_data = defaultdict(float)

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product = row['product']
        amount = float(row['amount'])
        sales_data[product] += amount

# 按总销售额降序排序
sorted_sales = dict(sorted(sales_data.items(), key=lambda x: x[1], reverse=True))

# 确保 output 目录存在
import os
os.makedirs('output', exist_ok=True)

# 写入 JSON 文件
with open('output/result.json', 'w') as f:
    json.dump(sorted_sales, f)

print("计算完成，结果已写入 output/result.json")
print("结果:", sorted_sales)