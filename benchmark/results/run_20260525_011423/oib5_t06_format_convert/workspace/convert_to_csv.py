import json
import csv

# 读取JSON文件
with open('data.json', 'r') as f:
    data = json.load(f)

# 定义CSV列顺序
fieldnames = ['id', 'name', 'category', 'price', 'in_stock']

# 写入CSV文件
with open('data.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 处理每一行数据
    for item in data:
        # 创建新字典以保持列顺序
        row = {}
        row['id'] = item['id']
        row['name'] = item['name']
        row['category'] = item['category']
        # price保留两位小数
        row['price'] = '{:.2f}'.format(float(item['price']))
        # in_stock转为yes/no
        row['in_stock'] = 'yes' if item['in_stock'] else 'no'
        
        writer.writerow(row)

print(f'转换完成，共处理了 {len(data)} 条记录')