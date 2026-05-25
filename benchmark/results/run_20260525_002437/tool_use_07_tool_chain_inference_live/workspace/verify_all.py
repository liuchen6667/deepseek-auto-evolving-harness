import json
from collections import defaultdict

# 读取原始数据
with open('sales_data.json', 'r') as f:
    sales = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 计算所有品类
category_stats = defaultdict(lambda: {'net_sales': 0.0, 'valid_orders': 0, 'orders': []})
cancelled_orders = set()

for order in sales:
    order_id = order['order_id']
    category = order['category']
    original_amount = order['quantity'] * order['unit_price']
    adjusted_amount = original_amount
    is_cancelled = False
    
    # 应用调整
    for adj in adjustments:
        if adj['order_id'] == order_id:
            if adj['type'] == 'cancelled':
                is_cancelled = True
                cancelled_orders.add(order_id)
            elif adj['type'] == 'partial_refund':
                adjusted_amount += adj['amount_delta']
    
    if not is_cancelled:
        category_stats[category]['net_sales'] += adjusted_amount
        category_stats[category]['valid_orders'] += 1
        category_stats[category]['orders'].append({
            'order_id': order_id,
            'adjusted_amount': adjusted_amount,
            'product': order['product']
        })

print("所有品类统计:")
for category, stats in category_stats.items():
    avg = stats['net_sales'] / stats['valid_orders'] if stats['valid_orders'] > 0 else 0
    print(f"{category}: 净销售额={stats['net_sales']}, 有效订单={stats['valid_orders']}, 平均订单额={avg:.2f}")
    
    # 找出最大订单
    max_order = max(stats['orders'], key=lambda x: x['adjusted_amount']) if stats['orders'] else None
    if max_order:
        print(f"  最大订单: {max_order['order_id']} ({max_order['product']}) = {max_order['adjusted_amount']}")
    print()

# 排序
sorted_categories = sorted(category_stats.items(), key=lambda x: (-x[1]['net_sales'], x[0]))
print("排序结果:")
for i, (category, stats) in enumerate(sorted_categories, 1):
    print(f"{i}. {category}: {stats['net_sales']}")

print(f"\n取消的订单: {sorted(list(cancelled_orders))}")

# 验证前3名差额
if len(sorted_categories) >= 2:
    winner_margin = sorted_categories[0][1]['net_sales'] - sorted_categories[1][1]['net_sales']
    print(f"\n第一名与第二名差额: {winner_margin}")
    print(f"Electronics ({sorted_categories[0][1]['net_sales']}) - Clothing ({sorted_categories[1][1]['net_sales']}) = {winner_margin}")