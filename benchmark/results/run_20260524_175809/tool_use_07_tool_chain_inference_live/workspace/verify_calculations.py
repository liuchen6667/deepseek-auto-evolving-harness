import json

# 读取数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 创建订单查找字典
orders_by_id = {order['order_id']: order for order in sales_data}
adj_by_id = {adj['order_id']: adj for adj in adjustments}

# 检查特定订单
print("检查调整订单:")
print("=" * 50)

for order_id in ['ORD006', 'ORD014', 'ORD015', 'ORD017']:
    if order_id in orders_by_id:
        order = orders_by_id[order_id]
        original_amount = order['quantity'] * order['unit_price']
        print(f"{order_id}: {order['category']} - {order['product']}")
        print(f"  原始金额: {order['quantity']} × {order['unit_price']} = {original_amount:.2f}")
        
        if order_id in adj_by_id:
            adj = adj_by_id[order_id]
            print(f"  调整类型: {adj['type']}")
            print(f"  调整金额: {adj['amount_delta']:.2f}")
            adjusted_amount = original_amount + adj['amount_delta']
            print(f"  调整后金额: {adjusted_amount:.2f}")
            if adj['type'] == 'cancelled':
                print(f"  → 此订单被完全取消，不计入统计")
        else:
            print(f"  无调整")
        print()

# 检查Electronics品类订单
print("\nElectronics品类订单详情:")
print("=" * 50)

electronics_orders = [o for o in sales_data if o['category'] == 'Electronics']
electronics_total = 0
for order in electronics_orders:
    order_id = order['order_id']
    original_amount = order['quantity'] * order['unit_price']
    adjusted_amount = original_amount
    
    if order_id in adj_by_id:
        adj = adj_by_id[order_id]
        if adj['type'] == 'partial_refund':
            adjusted_amount = original_amount + adj['amount_delta']
        elif adj['type'] == 'cancelled':
            adjusted_amount = 0
    
    electronics_total += adjusted_amount
    
    print(f"{order_id}: {order['product']}")
    print(f"  原始: {order['quantity']} × {order['unit_price']} = {original_amount:.2f}")
    if order_id in adj_by_id:
        adj = adj_by_id[order_id]
        print(f"  调整: {adj['type']} {adj['amount_delta']:.2f}")
    print(f"  调整后: {adjusted_amount:.2f}")
    print()

print(f"Electronics总净销售额: {electronics_total:.2f}")

# 检查Clothing品类订单
print("\nClothing品类订单详情:")
print("=" * 50)

clothing_orders = [o for o in sales_data if o['category'] == 'Clothing']
clothing_total = 0
for order in clothing_orders:
    order_id = order['order_id']
    original_amount = order['quantity'] * order['unit_price']
    adjusted_amount = original_amount
    
    if order_id in adj_by_id:
        adj = adj_by_id[order_id]
        if adj['type'] == 'partial_refund':
            adjusted_amount = original_amount + adj['amount_delta']
        elif adj['type'] == 'cancelled':
            adjusted_amount = 0
    
    clothing_total += adjusted_amount
    
    print(f"{order_id}: {order['product']}")
    print(f"  原始: {order['quantity']} × {order['unit_price']} = {original_amount:.2f}")
    if order_id in adj_by_id:
        adj = adj_by_id[order_id]
        print(f"  调整: {adj['type']} {adj['amount_delta']:.2f}")
    print(f"  调整后: {adjusted_amount:.2f}")
    print()

print(f"Clothing总净销售额: {clothing_total:.2f}")
