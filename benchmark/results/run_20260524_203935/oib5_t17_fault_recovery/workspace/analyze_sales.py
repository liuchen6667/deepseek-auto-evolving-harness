#!/usr/bin/env python3
import csv
import json
from collections import defaultdict

def analyze_sales():
    # 读取 CSV 文件
    product_totals = defaultdict(float)
    
    with open('data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product = row['product']
            amount = float(row['amount'])
            product_totals[product] += amount
    
    # 按总销售额降序排序
    sorted_totals = dict(sorted(
        product_totals.items(), 
        key=lambda x: x[1], 
        reverse=True
    ))
    
    # 确保金额是整数（如果数据是整数的话）
    # 如果所有金额都是整数，则输出整数
    result = {}
    for product, total in sorted_totals.items():
        if total.is_integer():
            result[product] = int(total)
        else:
            result[product] = total
    
    # 写入 JSON 文件
    with open('output/result.json', 'w') as jsonfile:
        json.dump(result, jsonfile, indent=2)
    
    print("分析完成！结果已保存到 output/result.json")
    print("\n产品销售额统计：")
    for product, total in result.items():
        print(f"  {product}: {total}")

if __name__ == "__main__":
    analyze_sales()