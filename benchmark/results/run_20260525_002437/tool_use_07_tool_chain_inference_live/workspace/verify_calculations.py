import json

# 读取原始数据
with open('sales_data.json', 'r') as f:
    sales = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 计算Electronics品类
electronics_orders = []
for order in sales:
    if order['category'] == 'Electronics':
        order_id = order['order_id']
        original_amount = order['quantity'] * order['unit_price']
        adjusted_amount = original_amount
        
        # 应用调整
        for adj in adjustments:
            if adj['order_id'] == order_id:
                if adj['type'] == 'partial_refund':
                    adjusted_amount += adj['amount_delta']
                elif adj['type'] == 'cancelled':
                    adjusted_amount = 0  # 将被排除
        
        # 只添加未取消的订单
        cancelled = any(adj['order_id'] == order_id and adj['type'] == 'cancelled' for adj in adjustments)
        if not cancelled:
            electronics_orders.append({
                'order_id': order_id,
                'original': original_amount,
                'adjusted': adjusted_amount
            })

print("Electronics订单详情:")
total_net = 0
for order in electronics_orders:
    print(f"  {order['order_id']}: 原始={order['original']}, 调整后={order['adjusted']}")
    total_net += order['adjusted']

print(f"\nElectronics净销售额: {total_net}")
print(f"订单数量: {len(electronics_orders)}")

# 检查ORD014
print("\n检查ORD014:")
for order in sales:
    if order['order_id'] == 'ORD014':
        original = order['quantity'] * order['unit_price']
        print(f"  ORD014原始: 10 * 50 = {original}")
        
for adj in adjustments:
    if adj['order_id'] == 'ORD014':
        print(f"  调整: {adj['type']}, amount_delta: {adj['amount_delta']}")
        print(f"  调整后金额: {original} + {adj['amount_delta']} = {original + adj['amount_delta']}")

# 检查被取消的订单
print("\n被取消的订单:")
cancelled = []
for adj in adjustments:
    if adj['type'] == 'cancelled':
        cancelled.append(adj['order_id'])
        for order in sales:
            if order['order_id'] == adj['order_id']:
                original = order['quantity'] * order['unit_price']
                print(f"  {adj['order_id']}: 原始金额={original}, 原因={adj['reason']}")

print(f"取消订单列表: {cancelled}")