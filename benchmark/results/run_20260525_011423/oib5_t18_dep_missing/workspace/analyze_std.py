"""分析脚本 — 使用 Python 标准库 csv 模块"""
import csv
import json
from collections import defaultdict

# 读取 CSV 文件并计算每个类别的金额总和
category_totals = defaultdict(float)

with open("data.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row["category"]
        amount = float(row["amount"])
        category_totals[category] += amount

# 将 defaultdict 转换为普通字典
result = dict(category_totals)

# 保存结果到 JSON 文件
with open("result.json", "w") as f:
    json.dump(result, f, indent=2)

print("Done:", result)
