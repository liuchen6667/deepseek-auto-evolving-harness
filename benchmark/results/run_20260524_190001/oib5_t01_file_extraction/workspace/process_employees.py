import csv
import json

# 读取 CSV 文件
with open('employees.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    employees = list(reader)

# 将 salary 转换为整数并筛选大于 80000 的员工
high_earners = []
for emp in employees:
    salary = int(emp['salary'])
    if salary > 80000:
        emp['salary'] = salary  # 转换为整数类型
        high_earners.append(emp)

# 按 salary 从高到低排序
high_earners.sort(key=lambda x: x['salary'], reverse=True)

# 保存为 JSON 文件
with open('high_earners.json', 'w') as jsonfile:
    json.dump(high_earners, jsonfile, indent=2)

# 打印结果
print(f"找到 {len(high_earners)} 位薪资超过 80000 的员工:")
for emp in high_earners:
    print(f"  {emp['name']}: {emp['department']}, ${emp['salary']}, {emp['start_date']}")
