#!/usr/bin/env python3
import csv
import json
import os
from collections import defaultdict

def main():
    # 读取数据
    sales_by_product = defaultdict(float)
    
    with open('data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row['product']
            amount = float(row['amount'])
            sales_by_product[product] += amount
    
    # 按销售额降序排序
    sorted_sales = dict(sorted(
        sales_by_product.items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    
    # 确保输出目录存在
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 写入 JSON 文件
    output_file = os.path.join(output_dir, 'result.json')
    with open(output_file, 'w') as f:
        json.dump(sorted_sales, f, indent=2)
    
    print(f"结果已保存到 {output_file}")
    print("产品销售额统计:")
    for product, total in sorted_sales.items():
        print(f"  {product}: {total}")

if __name__ == '__main__':
    main()