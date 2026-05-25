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

# 转换为 JSON 格式
json_data = json.dumps(high_earners_sorted, indent=2)

# 保存到文件
with open('high_earners.json', 'w') as jsonfile:
    jsonfile.write(json_data)

print(f'找到 {len(high_earners_sorted)} 名高薪员工，已保存到 high_earners.json')
print('高薪员工列表（按薪资从高到低排序）:')
for emp in high_earners_sorted:
    print(f"  {emp['name']}: {emp['department']}, ${emp['salary']}, {emp['start_date']}")