import json
from collections import defaultdict

# 加载数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 创建调整字典
adjustments_dict = {}
cancelled_orders = []
refund_orders = []

for adj in adjustments:
    order_id = adj['order_id']
    adjustments_dict[order_id] = adj
    if adj['type'] == 'cancelled':
        cancelled_orders.append(order_id)
    elif adj['type'] == 'partial_refund':
        refund_orders.append(order_id)

# 计算每个订单的原始金额
order_data = {}
for order in sales_data:
    order_id = order['order_id']
    original_amount = order['quantity'] * order['unit_price']
    order_data[order_id] = {
        'category': order['category'],
        'product': order['product'],
        'original_amount': original_amount,
        'adjusted_amount': original_amount,  # 初始化为原始金额
        'is_cancelled': False
    }

# 应用调整
for order_id, adj in adjustments_dict.items():
    if order_id in order_data:
        if adj['type'] == 'cancelled':
            order_data[order_id]['is_cancelled'] = True
            order_data[order_id]['adjusted_amount'] = 0
        elif adj['type'] == 'partial_refund':
            # 部分退款：从订单金额中扣除
            order_data[order_id]['adjusted_amount'] += adj['amount_delta']

# 按品类汇总
category_stats = defaultdict(lambda: {
    'net_sales': 0.0,
    'valid_order_count': 0,
    'orders': [],
    'largest_order': None
})

for order_id, data in order_data.items():
    category = data['category']
    
    # 如果订单被取消，跳过（不参与统计）
    if data['is_cancelled']:
        continue
    
    # 添加到品类统计
    category_stats[category]['net_sales'] += data['adjusted_amount']
    category_stats[category]['valid_order_count'] += 1
    category_stats[category]['orders'].append({
        'order_id': order_id,
        'product': data['product'],
        'adjusted_amount': data['adjusted_amount']
    })
    
    # 更新最大订单
    current_largest = category_stats[category]['largest_order']
    if current_largest is None or data['adjusted_amount'] > current_largest['adjusted_amount']:
        category_stats[category]['largest_order'] = {
            'order_id': order_id,
            'product': data['product'],
            'adjusted_amount': data['adjusted_amount']
        }

# 准备排序
categories_list = []
for category, stats in category_stats.items():
    categories_list.append({
        'category': category,
        'net_sales': round(stats['net_sales'], 2),
        'valid_order_count': stats['valid_order_count'],
        'average_order_amount': round(stats['net_sales'] / stats['valid_order_count'], 2) if stats['valid_order_count'] > 0 else 0.0,
        'largest_order': stats['largest_order']
    })

# 排序：按净销售额降序，如果相同按品类名字母序升序
categories_list.sort(key=lambda x: (-x['net_sales'], x['category']))

# 取前3个
top_categories = categories_list[:3]

# 准备报告
ranking_basis = "net_sales_after_adjustments"

# 构建 top_categories 格式
formatted_top_categories = []
for i, cat in enumerate(top_categories, 1):
    formatted_top_categories.append({
        'rank': i,
        'category': cat['category'],
        'net_sales': cat['net_sales'],
        'valid_order_count': cat['valid_order_count'],
        'average_order_amount': cat['average_order_amount'],
        'largest_order': {
            'order_id': cat['largest_order']['order_id'],
            'product': cat['largest_order']['product'],
            'amount': round(cat['largest_order']['adjusted_amount'], 2)
        }
    })

# dropped_orders: 完全取消的订单
dropped_orders = cancelled_orders

# adjustment_summary
adjustment_summary = {
    'refund_order_ids': refund_orders,
    'cancelled_order_ids': cancelled_orders
}

# summary
evaluated_categories = len(category_stats)
top_category = top_categories[0]['category'] if top_categories else ""
winner_margin_vs_runner_up = 0.0
if len(top_categories) >= 2:
    winner_margin_vs_runner_up = round(top_categories[0]['net_sales'] - top_categories[1]['net_sales'], 2)

summary = {
    'evaluated_categories': evaluated_categories,
    'top_category': top_category,
    'winner_margin_vs_runner_up': winner_margin_vs_runner_up
}

# evidence_refs
evidence_refs = [
    "sales_data.json: raw order records with category, product, quantity, unit_price",
    "adjustments.json: adjustment events (partial_refund, cancelled) with amount_delta",
    "analysis_brief.md: definition of net_sales, cancelled/partial_refund policies, sorting rules"
]

# 构建最终报告
report = {
    'ranking_basis': ranking_basis,
    'top_categories': formatted_top_categories,
    'dropped_orders': dropped_orders,
    'adjustment_summary': adjustment_summary,
    'summary': summary,
    'evidence_refs': evidence_refs
}

# 写入文件
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Report generated successfully!")
print(f"Top categories: {[cat['category'] for cat in top_categories]}")
print(f"Dropped orders: {dropped_orders}")