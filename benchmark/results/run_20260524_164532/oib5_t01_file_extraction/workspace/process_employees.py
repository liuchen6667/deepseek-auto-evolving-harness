import csv
import json

# 读取CSV文件
with open('employees.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    employees = []
    
    for row in reader:
        # 转换salary为整数
        row['salary'] = int(row['salary'])
        employees.append(row)

# 筛选salary大于80000的员工
high_earners = [emp for emp in employees if emp['salary'] > 80000]

# 按salary从高到低排序
high_earners_sorted = sorted(high_earners, key=lambda x: x['salary'], reverse=True)

# 准备JSON输出
output_data = []
for emp in high_earners_sorted:
    output_data.append({
        'name': emp['name'],
        'department': emp['department'],
        'salary': emp['salary'],
        'start_date': emp['start_date']
    })

# 写入JSON文件
with open('high_earners.json', 'w') as jsonfile:
    json.dump(output_data, jsonfile, indent=2)

print(f'找到 {len(high_earners_sorted)} 个salary大于80000的员工')
print('结果已保存到 high_earners.json')

# 显示结果
for i, emp in enumerate(high_earners_sorted, 1):
    print(f"{i}. {emp['name']}: {emp['department']}, ${emp['salary']}, {emp['start_date']}")