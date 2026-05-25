import json

# 读取销售数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

# 读取调整数据
with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 创建调整字典
adjustment_dict = {}
cancelled_orders = []
refund_orders = []

for adj in adjustments:
    order_id = adj['order_id']
    adjustment_dict[order_id] = adj
    if adj['type'] == 'cancelled':
        cancelled_orders.append(order_id)
    elif adj['type'] == 'partial_refund':
        refund_orders.append(order_id)

# 计算每个订单的原始金额和调整后金额
order_details = {}
for order in sales_data:
    order_id = order['order_id']
    original_amount = order['quantity'] * order['unit_price']
    
    if order_id in adjustment_dict:
        adj = adjustment_dict[order_id]
        if adj['type'] == 'cancelled':
            # 整单作废，不参与统计
            adjusted_amount = None  # 标记为无效
        elif adj['type'] == 'partial_refund':
            adjusted_amount = original_amount + adj['amount_delta']
    else:
        adjusted_amount = original_amount
    
    order_details[order_id] = {
        'order_id': order_id,
        'category': order['category'],
        'product': order['product'],
        'original_amount': original_amount,
        'adjusted_amount': adjusted_amount,
        'is_valid': adjusted_amount is not None
    }

# 按品类汇总
category_stats = {}
for order_id, details in order_details.items():
    if not details['is_valid']:
        continue  # 跳过取消的订单
    
    category = details['category']
    if category not in category_stats:
        category_stats[category] = {
            'net_sales': 0.0,
            'valid_order_count': 0,
            'orders': []  # 保存调整后的金额用于找最大订单
        }
    
    category_stats[category]['net_sales'] += details['adjusted_amount']
    category_stats[category]['valid_order_count'] += 1
    category_stats[category]['orders'].append({
        'order_id': order_id,
        'product': details['product'],
        'adjusted_amount': details['adjusted_amount']
    })

# 对每个品类找最大订单
for category in category_stats:
    orders = category_stats[category]['orders']
    largest_order = max(orders, key=lambda x: x['adjusted_amount'])
    category_stats[category]['largest_order'] = largest_order
    # 计算平均订单金额
    if category_stats[category]['valid_order_count'] > 0:
        category_stats[category]['average_order_amount'] = category_stats[category]['net_sales'] / category_stats[category]['valid_order_count']
    else:
        category_stats[category]['average_order_amount'] = 0.0

# 按净销售额排序，如果相同按品类名字母序
sorted_categories = sorted(category_stats.items(), 
                          key=lambda x: (-x[1]['net_sales'], x[0]))

print('Category statistics:')
for i, (category, stats) in enumerate(sorted_categories, 1):
    print(f'{i}. {category}: net_sales={stats["net_sales"]:.2f}, valid_orders={stats["valid_order_count"]}, avg_order={stats["average_order_amount"]:.2f}')
    print(f'   Largest order: {stats["largest_order"]["order_id"]} - {stats["largest_order"]["product"]} (${stats["largest_order"]["adjusted_amount"]:.2f})')

print(f'\nCancelled orders: {cancelled_orders}')
print(f'Refund orders: {refund_orders}')

# 输出前3个品类
top_3 = sorted_categories[:3]
print('\nTop 3 categories:')
for i, (category, stats) in enumerate(top_3, 1):
    print(f'{i}. {category}: ${stats["net_sales"]:.2f}')

# 计算总结数据
evaluated_categories = len(category_stats)
if len(top_3) >= 2:
    winner_margin = top_3[0][1]['net_sales'] - top_3[1][1]['net_sales']
else:
    winner_margin = 0.0

print(f'\nSummary:')
print(f'Evaluated categories: {evaluated_categories}')
print(f'Top category: {top_3[0][0] if top_3 else "N/A"}')
print(f'Winner margin vs runner up: {winner_margin:.2f}')

# 验证数据
print('\nOrder details:')
for order_id, details in order_details.items():
    status = 'valid' if details['is_valid'] else 'cancelled'
    adj_amount = details['adjusted_amount'] if details['adjusted_amount'] is not None else 'N/A'
    print(f'{order_id}: {details["category"]} - {details["product"]}, original=${details["original_amount"]:.2f}, adjusted={adj_amount}, status={status}')