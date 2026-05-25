import json
import csv

# 读取 JSON 文件
with open('data.json', 'r') as f:
    data = json.load(f)

# 定义输出 CSV 文件
output_file = 'data.csv'

# 定义列顺序
columns = ['id', 'name', 'category', 'price', 'in_stock']

# 写入 CSV 文件
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    for item in data:
        # 创建新的字典，确保列顺序
        row = {}
        for col in columns:
            if col == 'price':
                # price 保留两位小数
                row[col] = f"{item[col]:.2f}"
            elif col == 'in_stock':
                # in_stock 转为 yes/no
                row[col] = 'yes' if item[col] else 'no'
            else:
                row[col] = item[col]
        writer.writerow(row)

print(f"CSV 文件已生成: {output_file}")
print(f"共转换了 {len(data)} 条记录")
