import json
import csv

# 读取 orders.json
with open('orders.json', 'r') as f:
    orders = json.load(f)

# 过滤条件：tier=vip 且 total >= 100
filtered_orders = [
    order for order in orders 
    if order['tier'] == 'vip' and order['total'] >= 100
]

# 按 total 降序排序
filtered_orders.sort(key=lambda x: x['total'], reverse=True)

# 写入 CSV 文件
with open('vip_orders.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    # 写入表头
    writer.writerow(['order_id', 'total'])
    
    # 写入数据行
    for order in filtered_orders:
        writer.writerow([order['order_id'], order['total']])

# 输出结果统计
print(f'处理完成！符合条件的订单数量：{len(filtered_orders)}')
for order in filtered_orders:
    print(f"  {order['order_id']}: {order['total']}")