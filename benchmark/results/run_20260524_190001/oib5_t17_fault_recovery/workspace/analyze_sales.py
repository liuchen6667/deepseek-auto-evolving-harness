import csv
import json
from collections import defaultdict

# 读取CSV文件
product_totals = defaultdict(float)

with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product = row['product']
        amount = float(row['amount'])
        product_totals[product] += amount

# 按销售额降序排序
sorted_products = dict(sorted(product_totals.items(), key=lambda x: x[1], reverse=True))

# 写入JSON文件
with open('output/result.json', 'w') as f:
    json.dump(sorted_products, f, indent=2)

print(f"分析完成！共处理了 {len(product_totals)} 个产品的数据")
print(f"结果已保存到 output/result.json")
print("\n每个产品的总销售额：")
for product, total in sorted_products.items():
    print(f"  {product}: {total}")