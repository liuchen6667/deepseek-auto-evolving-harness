import json
import csv
import sys

# 读取 orders.json
with open('orders.json', 'r') as f:
    orders = json.load(f)

# 过滤订单：tier=vip 且 total >= 100
filtered_orders = [
    order for order in orders 
    if order.get('tier') == 'vip' and order.get('total', 0) >= 100
]

# 按 total 降序排序
sorted_orders = sorted(filtered_orders, key=lambda x: x['total'], reverse=True)

# 写入 CSV 文件
with open('vip_orders.csv', 'w', newline='') as csvfile:
    fieldnames = ['order_id', 'total']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for order in sorted_orders:
        writer.writerow({'order_id': order['order_id'], 'total': order['total']})

print(f"处理完成！共写入 {len(sorted_orders)} 行数据（不含表头）")
print(f"符合条件的订单：{sorted_orders}")