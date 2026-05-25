import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as json_file:
    data = json.load(json_file)

# 准备 CSV 文件
with open('data.csv', 'w', newline='') as csv_file:
    # 定义表头
    fieldnames = ['id', 'name', 'category', 'price', 'in_stock']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    for item in data:
        # 创建新行，处理 price 和 in_stock
        row = {
            'id': item['id'],
            'name': item['name'],
            'category': item['category'],
            'price': f"{item['price']:.2f}",  # 保留两位小数
            'in_stock': 'yes' if item['in_stock'] else 'no'  # 转换为 yes/no
        }
        writer.writerow(row)

print(f"已成功转换 {len(data)} 条记录到 data.csv")
print("列顺序: id, name, category, price, in_stock")
print("price 已格式化为两位小数")
print("in_stock 已转换为 yes/no")
