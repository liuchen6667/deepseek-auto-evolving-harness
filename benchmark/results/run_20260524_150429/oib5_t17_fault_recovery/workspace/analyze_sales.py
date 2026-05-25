#!/usr/bin/env python3
import csv
import json
import os

def analyze_sales():
    # 定义文件路径
    data_file = "data.csv"
    output_dir = "output"
    output_file = os.path.join(output_dir, "result.json")
    
    # 读取CSV文件
    product_totals = {}
    
    with open(data_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = row['product']
            amount = float(row['amount'])
            
            if product in product_totals:
                product_totals[product] += amount
            else:
                product_totals[product] = amount
    
    # 按总销售额降序排序
    sorted_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
    
    # 创建排序后的字典
    result = {product: total for product, total in sorted_products}
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 写入JSON文件
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"分析完成！结果已保存到 {output_file}")
    print(f"每个产品的总销售额：")
    for product, total in sorted_products:
        print(f"  {product}: {total}")

if __name__ == "__main__":
    analyze_sales()