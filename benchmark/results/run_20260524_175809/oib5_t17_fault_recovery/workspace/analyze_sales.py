import csv
import json
from collections import defaultdict

# 读取CSV文件
product_sales = defaultdict(float)

with open('data.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        product = row['product']
        amount = float(row['amount'])
        product_sales[product] += amount

# 按总销售额降序排序
sorted_products = dict(sorted(product_sales.items(), key=lambda x: x[1], reverse=True))

# 写入JSON文件
with open('output/result.json', 'w') as json_file:
    json.dump(sorted_products, json_file, indent=2)

print("分析完成！结果已保存到 output/result.json")
print("各产品总销售额：")
for product, total in sorted_products.items():
    print(f"  {product}: {total}")