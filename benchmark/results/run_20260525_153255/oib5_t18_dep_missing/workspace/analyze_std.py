"""分析脚本 — 使用 Python 标准库 csv 模块"""
import csv
import json

# 用于存储每个 category 的 amount 总和
category_sums = {}

# 读取 CSV 文件
with open("data.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    
    # 遍历每一行数据
    for row in reader:
        category = row["category"]
        amount = int(row["amount"])  # 转换为整数类型
        
        # 累加到对应的 category
        if category in category_sums:
            category_sums[category] += amount
        else:
            category_sums[category] = amount

# 按照原始脚本的输出顺序对结果进行排序
# 原始顺序是：Books, Clothing, Electronics
sorted_categories = ["Books", "Clothing", "Electronics"]
sorted_result = {}
for category in sorted_categories:
    if category in category_sums:
        sorted_result[category] = category_sums[category]

# 将结果写入 JSON 文件
with open("result.json", "w") as f:
    json.dump(sorted_result, f, indent=2)

print("Done:", sorted_result)