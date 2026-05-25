#!/usr/bin/env python3
import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 定义输出 CSV 文件名
output_file = 'data.csv'

# 定义列顺序
fieldnames = ['id', 'name', 'category', 'price', 'in_stock']

# 写入 CSV 文件
with open(output_file, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 处理每条记录
    for item in data:
        # 创建新字典，确保列顺序
        row = {}
        
        # 处理每个字段
        for field in fieldnames:
            if field == 'price':
                # price 保留两位小数
                row[field] = f"{item[field]:.2f}"
            elif field == 'in_stock':
                # in_stock 转为 "yes"/"no"
                row[field] = 'yes' if item[field] else 'no'
            else:
                # 其他字段保持原样
                row[field] = item[field]
        
        # 写入行
        writer.writerow(row)

print(f"CSV 文件已生成: {output_file}")
print(f"处理了 {len(data)} 条记录")
