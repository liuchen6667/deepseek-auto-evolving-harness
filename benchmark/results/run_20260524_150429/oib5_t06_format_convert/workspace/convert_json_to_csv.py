import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 定义 CSV 文件名和表头
csv_filename = 'data.csv'
fieldnames = ['id', 'name', 'category', 'price', 'in_stock']

# 写入 CSV 文件
with open(csv_filename, 'w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    for item in data:
        # 创建新行，处理 price 和 in_stock 字段
        row = {
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'price': f"{item['price']:.2f}",  # 保留两位小数
            'in_stock': 'yes' if item['in_stock'] else 'no'  # 转换为 yes/no
        }
        writer.writerow(row)

print(f'转换完成！已创建 {csv_filename}')
print(f'共转换了 {len(data)} 条记录')