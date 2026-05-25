#!/usr/bin/env python3
import csv
import json
from datetime import datetime

# 读取CSV文件
employees = []
with open('employees.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 将salary转换为整数
        row['salary'] = int(row['salary'])
        employees.append(row)

# 筛选salary大于80000的员工
high_earners = [emp for emp in employees if emp['salary'] > 80000]

# 按salary从高到低排序
high_earners.sort(key=lambda x: x['salary'], reverse=True)

# 准备JSON输出
output_data = []
for emp in high_earners:
    output_data.append({
        'name': emp['name'],
        'department': emp['department'],
        'salary': emp['salary'],
        'start_date': emp['start_date']
    })

# 保存为JSON文件
with open('high_earners.json', 'w') as f:
    json.dump(output_data, f, indent=2)

# 打印结果
print(f"总共找到 {len(high_earners)} 位薪资超过80000的员工:")
for emp in output_data:
    print(f"  {emp['name']}: {emp['department']}, ${emp['salary']}, {emp['start_date']}")