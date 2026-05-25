#!/usr/bin/env python3
"""分析脚本 — 使用 Python 标准库 csv 模块"""
import csv
import json
from collections import defaultdict

# 读取 CSV 文件
category_sums = defaultdict(float)

with open('data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row['category']
        amount = float(row['amount'])
        category_sums[category] += amount

# 转换为普通字典（可选）
result = dict(category_sums)

# 将结果保存到 JSON 文件
with open('result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Done:", result)