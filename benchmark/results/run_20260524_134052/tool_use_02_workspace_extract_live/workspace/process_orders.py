import json
import csv

# 读取 orders.json
with open('orders.json', 'r') as f:
    orders = json.load(f)

# 过滤条件: tier=vip 且 total >= 100
filtered_orders = [
    order for order in orders 
    if order['tier'] == 'vip' and order['total'] >= 100
]

# 按 total 降序排序
filtered_orders.sort(key=lambda x: x['total'], reverse=True)

# 只保留 order_id 和 total 字段
processed_orders = [
    {'order_id': order['order_id'], 'total': order['total']}
    for order in filtered_orders
]

# 写入 CSV 文件
with open('vip_orders.csv', 'w', newline='') as csvfile:
    fieldnames = ['order_id', 'total']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # 写入表头
    writer.writeheader()
    
    # 写入数据行
    writer.writerows(processed_orders)

# 输出统计信息
print(f"处理完成！共写入 {len(processed_orders)} 行数据（不含表头）")
print(f"符合条件的订单: {[order['order_id'] for order in processed_orders]}")