import csv
import json

# 读取 CSV 文件
with open('employees.csv', 'r') as f:
    reader = csv.DictReader(f)
    employees = list(reader)

# 筛选 salary > 80000 的员工，将 salary 转换为整数
high_earners = []
for emp in employees:
    salary = int(emp['salary'])
    if salary > 80000:
        emp['salary'] = salary  # 确保 salary 是数字类型
        high_earners.append(emp)

# 按 salary 从高到低排序
high_earners.sort(key=lambda x: x['salary'], reverse=True)

# 打印筛选结果
print(f'找到 {len(high_earners)} 位高薪员工:')
for emp in high_earners:
    print(f"{emp['name']}: {emp['department']}, {emp['salary']}, {emp['start_date']}")

# 准备 JSON 数据
json_data = []
for emp in high_earners:
    json_data.append({
        'name': emp['name'],
        'department': emp['department'],
        'salary': emp['salary'],
        'start_date': emp['start_date']
    })

print('\nJSON 数据:')
print(json.dumps(json_data, indent=2))

# 保存到文件
with open('high_earners.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print('\n已保存到 high_earners.json')