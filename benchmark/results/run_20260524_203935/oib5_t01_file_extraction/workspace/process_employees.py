import csv
import json

# 读取 CSV 文件
employees = []
with open('employees.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # 将 salary 转换为整数
        row['salary'] = int(row['salary'])
        employees.append(row)

# 筛选 salary > 80000 的员工
high_earners = [emp for emp in employees if emp['salary'] > 80000]

# 按 salary 从高到低排序
high_earners_sorted = sorted(high_earners, key=lambda x: x['salary'], reverse=True)

# 创建符合要求的 JSON 结构
result = []
for emp in high_earners_sorted:
    result.append({
        'name': emp['name'],
        'department': emp['department'],
        'salary': emp['salary'],
        'start_date': emp['start_date']
    })

# 保存为 JSON 文件
with open('high_earners.json', 'w') as jsonfile:
    json.dump(result, jsonfile, indent=2)

print(f'找到 {len(result)} 位高薪员工，已保存到 high_earners.json')
print('\n高薪员工列表（按薪资从高到低排序）:')
for i, emp in enumerate(result, 1):
    print(f'{i}. {emp["name"]} - {emp["department"]} - ${emp["salary"]:,} - {emp["start_date"]}')
