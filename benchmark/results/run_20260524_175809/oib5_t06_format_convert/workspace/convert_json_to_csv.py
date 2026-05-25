#!/usr/bin/env python3
import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 定义表头顺序
header = ['id', 'name', 'category', 'price', 'in_stock']

# 转换数据
converted_data = []
for item in data:
    # 创建新行，确保顺序正确
    row = {
        'id': item['id'],
        'name': item['name'],
        'category': item['category'],
        'price': f"{item['price']:.2f}",  # 保留两位小数
        'in_stock': 'yes' if item['in_stock'] else 'no'  # 转换 true/false 为 yes/no
    }
    converted_data.append(row)

# 写入 CSV 文件
with open('data.csv', 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=header)
    writer.writeheader()
    writer.writerows(converted_data)

print(f"转换完成！共处理 {len(converted_data)} 条记录。")
print(f"CSV 文件已保存为 'data.csv'")