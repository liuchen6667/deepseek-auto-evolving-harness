#!/usr/bin/env python3
import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 指定输出字段和顺序
fieldnames = ['id', 'name', 'category', 'price', 'in_stock']

# 写入 CSV 文件
with open('data.csv', 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    for item in data:
        # 创建新行数据
        row = {
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'price': f"{item['price']:.2f}",  # 保留两位小数
            'in_stock': 'yes' if item['in_stock'] else 'no'  # 转为 yes/no
        }
        writer.writerow(row)

print(f"转换完成，共转换了 {len(data)} 条记录")
print("CSV 文件已保存为 data.csv")