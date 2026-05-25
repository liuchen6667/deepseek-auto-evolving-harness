import json

# 重新计算验证
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 计算每个订单的调整后金额
order_amounts = {}
for order in sales_data:
    order_id = order['order_id']
    amount = order['quantity'] * order['unit_price']
    order_amounts[order_id] = {
        'category': order['category'],
        'product': order['product'],
        'original': amount,
        'adjusted': amount
    }

# 应用调整
for adj in adjustments:
    order_id = adj['order_id']
    if adj['type'] == 'partial_refund':
        order_amounts[order_id]['adjusted'] += adj['amount_delta']
    elif adj['type'] == 'cancelled':
        order_amounts[order_id]['adjusted'] = 0

# 按品类汇总
category_totals = {}
category_valid_orders = {}
category_orders = {}

for order_id, details in order_amounts.items():
    category = details['category']
    if category not in category_totals:
        category_totals[category] = 0.0
        category_valid_orders[category] = 0
        category_orders[category] = []
    
    # 检查订单是否被取消
    is_cancelled = any(adj['order_id'] == order_id and adj['type'] == 'cancelled' for adj in adjustments)
    
    if not is_cancelled:
        category_totals[category] += details['adjusted']
        category_valid_orders[category] += 1
    
    category_orders[category].append({
        'order_id': order_id,
        'product': details['product'],
        'adjusted': details['adjusted'],
        'is_cancelled': is_cancelled
    })

print("Category totals:")
for category in sorted(category_totals.keys()):
    print(f"{category}: {category_totals[category]:.2f}, valid orders: {category_valid_orders[category]}")

print("\nOrder details by category:")
for category in sorted(category_totals.keys()):
    print(f"\n{category}:")
    valid_orders = [o for o in category_orders[category] if not o['is_cancelled']]
    if valid_orders:
        max_order = max(valid_orders, key=lambda x: x['adjusted'])
        print(f"  Max order: {max_order['order_id']} ({max_order['product']}): {max_order['adjusted']:.2f}")
    for order in sorted(category_orders[category], key=lambda x: x['order_id']):
        status = "CANCELLED" if order['is_cancelled'] else "active"
        print(f"  {order['order_id']}: {order['product']}: {order['adjusted']:.2f} ({status})")

# 验证报告中的值
with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

print("\nVerification:")
print(f"Top category margin: {report['summary']['winner_margin_vs_runner_up']}")
print(f"Expected margin: {category_totals['Electronics'] - category_totals['Clothing']:.2f}")

# 检查金额格式
print("\nChecking decimal places:")
for cat in report['top_categories']:
    print(f"{cat['category']}: net_sales={cat['net_sales']}, avg={cat['average_order_amount']}, largest={cat['largest_order']['amount']}")
    # 检查是否为2位小数
    if isinstance(cat['net_sales'], float):
        if cat['net_sales'] != round(cat['net_sales'], 2):
            print(f"  WARNING: net_sales not 2 decimal places: {cat['net_sales']}")