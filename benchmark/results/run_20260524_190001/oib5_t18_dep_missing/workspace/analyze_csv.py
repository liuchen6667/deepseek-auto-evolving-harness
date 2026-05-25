#!/usr/bin/env python3
"""分析脚本 — 使用标准库 csv 模块"""
import csv
import json

# 读取 CSV 文件并计算每个 category 的 amount 总和
category_totals = {}

with open('data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row['category']
        amount = int(row['amount'])  # 使用 int 而不是 float
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

# 将结果保存到 JSON 文件
with open('result.json', 'w') as f:
    json.dump(category_totals, f, indent=2)

print("Done:", category_totals)