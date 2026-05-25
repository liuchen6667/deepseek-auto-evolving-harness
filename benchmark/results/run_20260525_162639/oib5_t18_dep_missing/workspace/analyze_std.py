"""分析脚本 — 使用 Python 标准库"""
import csv
import json
from collections import defaultdict

# 读取 CSV 文件并计算每个 category 的 amount 总和
category_totals = defaultdict(int)

with open("data.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        category = row["category"]
        amount = int(row["amount"])
        category_totals[category] += amount

# 将 defaultdict 转换为普通字典
result = dict(category_totals)

# 保存结果到 result.json
with open("result.json", "w") as f:
    json.dump(result, f, indent=2)

print("Done:", result)