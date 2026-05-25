import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 定义 CSV 文件路径
csv_file = 'data.csv'

# 定义表头
fieldnames = ['id', 'name', 'category', 'price', 'in_stock']

# 写入 CSV 文件
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    for item in data:
        # 创建新行，转换数据格式
        row = {
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'price': f"{item['price']:.2f}",  # 保留两位小数
            'in_stock': 'yes' if item['in_stock'] else 'no'  # true->yes, false->no
        }
        writer.writerow(row)

print(f"CSV 文件已生成: {csv_file}")
print(f"转换了 {len(data)} 条记录")

# 显示前几行内容
print("\nCSV 文件内容预览:")
with open(csv_file, 'r') as f:
    for i, line in enumerate(f):
        if i < 5:  # 显示前5行
            print(line.strip())