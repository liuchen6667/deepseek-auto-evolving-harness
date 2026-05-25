import json
import math

# 读取数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

with open('report_contract.json', 'r') as f:
    contract = json.load(f)

# 创建调整映射
action_map = {}
refund_order_ids = []
cancelled_order_ids = []

for adj in adjustments:
    order_id = adj['order_id']
    action_map[order_id] = adj
    if adj['type'] == 'partial_refund':
        refund_order_ids.append(order_id)
    elif adj['type'] == 'cancelled':
        cancelled_order_ids.append(order_id)

# 初始化品类统计
category_stats = {}

# 处理每个订单
for order in sales_data:
    order_id = order['order_id']
    category = order['category']
    product = order['product']
    quantity = order['quantity']
    unit_price = order['unit_price']
    
    # 计算原始金额
    original_amount = quantity * unit_price
    
    # 检查是否有调整
    adjusted_amount = original_amount
    is_cancelled = False
    
    if order_id in action_map:
        adj = action_map[order_id]
        if adj['type'] == 'cancelled':
            is_cancelled = True
            adjusted_amount = 0
        elif adj['type'] == 'partial_refund':
            adjusted_amount = original_amount + adj['amount_delta']
    
    # 初始化品类统计（如果不存在）
    if category not in category_stats:
        category_stats[category] = {
            'net_sales': 0.0,
            'valid_order_count': 0,
            'orders': [],
            'largest_order': None
        }
    
    # 如果不是取消的订单，则计入统计
    if not is_cancelled:
        category_stats[category]['net_sales'] += adjusted_amount
        category_stats[category]['valid_order_count'] += 1
        
        # 记录订单详情（用于查找最大订单）
        order_info = {
            'order_id': order_id,
            'product': product,
            'adjusted_amount': adjusted_amount,
            'original_amount': original_amount
        }
        category_stats[category]['orders'].append(order_info)
        
        # 更新最大订单
        current_largest = category_stats[category]['largest_order']
        if current_largest is None or adjusted_amount > current_largest['adjusted_amount']:
            category_stats[category]['largest_order'] = {
                'order_id': order_id,
                'product': product,
                'adjusted_amount': adjusted_amount
            }

# 计算平均订单金额
for category in category_stats:
    stats = category_stats[category]
    if stats['valid_order_count'] > 0:
        stats['average_order_amount'] = stats['net_sales'] / stats['valid_order_count']
    else:
        stats['average_order_amount'] = 0.0

# 按净销售额排序（降序），如果相同按品类名字母序升序
sorted_categories = sorted(
    category_stats.items(),
    key=lambda x: (-x[1]['net_sales'], x[0])
)

# 输出前3个品类
top_3 = sorted_categories[:3]

print("品类统计:")
for i, (category, stats) in enumerate(sorted_categories, 1):
    print(f"{i}. {category}: 净销售额={stats['net_sales']:.2f}, 有效订单数={stats['valid_order_count']}, 平均订单金额={stats['average_order_amount']:.2f}")

print(f"\n前3个品类:")
for i, (category, stats) in enumerate(top_3, 1):
    largest = stats['largest_order']
    print(f"{i}. {category}: 净销售额={stats['net_sales']:.2f}")
    if largest:
        print(f"   最大订单: {largest['order_id']} - {largest['product']} - 金额={largest['adjusted_amount']:.2f}")

print(f"\n退款订单: {refund_order_ids}")
print(f"取消订单: {cancelled_order_ids}")
print(f"被丢弃的订单（完全取消）: {cancelled_order_ids}")

# 计算总结数据
evaluated_categories = len(category_stats)
if len(top_3) >= 2:
    winner_margin = top_3[0][1]['net_sales'] - top_3[1][1]['net_sales']
else:
    winner_margin = 0.0

print(f"\n总结:")
print(f"评估品类数: {evaluated_categories}")
print(f"顶级品类: {top_3[0][0] if top_3 else 'N/A'}")
print(f"冠军与亚军差距: {winner_margin:.2f}")
