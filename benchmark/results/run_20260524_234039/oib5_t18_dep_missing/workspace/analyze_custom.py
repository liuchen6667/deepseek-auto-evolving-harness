#!/usr/bin/env python3
"""分析脚本 — 使用标准库 csv 模块"""
import csv
import json

# 读取 CSV 文件并计算每个 category 的 amount 总和
category_totals = {}

with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row['category']
        amount = float(row['amount'])  # 转换为数字类型
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

# 确保结果为整数（与原始数据一致）
result = {category: int(total) for category, total in category_totals.items()}

# 按字母顺序排序键，以便结果一致
sorted_result = dict(sorted(result.items()))

# 保存结果到 result.json
with open('result.json', 'w') as f:
    json.dump(sorted_result, f, indent=2)

print("Done:", sorted_result)