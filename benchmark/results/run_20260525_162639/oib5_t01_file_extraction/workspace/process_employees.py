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
high_earners.sort(key=lambda x: x['salary'], reverse=True)

# 创建输出 JSON 结构
output_data = []
for emp in high_earners:
    output_data.append({
        'name': emp['name'],
        'department': emp['department'],
        'salary': emp['salary'],
        'start_date': emp['start_date']
    })

# 写入 JSON 文件
with open('high_earners.json', 'w') as jsonfile:
    json.dump(output_data, jsonfile, indent=2)

print(f"找到 {len(high_earners)} 位高薪员工，已保存到 high_earners.json")
print("员工列表（按薪资降序）：")
for emp in output_data:
    print(f"  {emp['name']}: {emp['department']}, ${emp['salary']}, {emp['start_date']}")