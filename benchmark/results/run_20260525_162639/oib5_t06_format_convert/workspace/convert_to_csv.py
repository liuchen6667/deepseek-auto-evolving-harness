import json
import csv

# 读取 JSON 数据
with open('data.json', 'r') as f:
    data = json.load(f)

# 定义输出文件
output_file = 'data.csv'

# 定义列顺序
fieldnames = ['id', 'name', 'category', 'price', 'in_stock']

# 写入 CSV 文件
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    
    for item in data:
        # 处理 price 保留两位小数
        item['price'] = f"{item['price']:.2f}"
        # 处理 in_stock 转为 yes/no
        item['in_stock'] = 'yes' if item['in_stock'] else 'no'
        writer.writerow(item)

print(f"CSV 文件已创建: {output_file}")
print(f"共转换了 {len(data)} 条记录")