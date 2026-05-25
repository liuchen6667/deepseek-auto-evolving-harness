#!/usr/bin/env python3
"""分析脚本 — 使用 Python 标准库 csv 模块"""
import csv
import json

# 初始化字典来存储每个类别的总和
category_sums = {}

# 读取 CSV 文件
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category = row['category']
        amount = int(row['amount'])  # 转换为整数类型
        
        # 累加到对应类别
        if category in category_sums:
            category_sums[category] += amount
        else:
            category_sums[category] = amount

# 将结果写入 JSON 文件
with open('result.json', 'w') as f:
    json.dump(category_sums, f, indent=2)

print("Done:", category_sums)
