import json
import os

# 读取数据
with open('sales_data.json', 'r') as f:
    sales = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 创建调整字典
adj_dict = {}
refund_order_ids = []
cancelled_order_ids = []
for adj in adjustments:
    order_id = adj['order_id']
    adj_dict[order_id] = adj
    if adj['type'] == 'partial_refund':
        refund_order_ids.append(order_id)
    elif adj['type'] == 'cancelled':
        cancelled_order_ids.append(order_id)

# 计算每个订单的原始金额和调整后金额
order_data = {}
for sale in sales:
    order_id = sale['order_id']
    original_amount = sale['quantity'] * sale['unit_price']
    
    # 初始化订单数据
    order_data[order_id] = {
        'category': sale['category'],
        'product': sale['product'],
        'original_amount': original_amount,
        'adjusted_amount': original_amount,
        'is_cancelled': False
    }

# 应用调整
for order_id, adj in adj_dict.items():
    if order_id not in order_data:
        continue
    
    if adj['type'] == 'partial_refund':
        order_data[order_id]['adjusted_amount'] += adj['amount_delta']
    elif adj['type'] == 'cancelled':
        order_data[order_id]['is_cancelled'] = True
        order_data[order_id]['adjusted_amount'] = 0  # 整单作废，不计入净销售额

# 按品类汇总
category_stats = {}
for order_id, data in order_data.items():
    category = data['category']
    if category not in category_stats:
        category_stats[category] = {
            'net_sales': 0.0,
            'valid_order_count': 0,
            'orders': [],  # 存储订单信息用于计算最大订单
            'category_name': category
        }
    
    # 如果订单被取消，跳过
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

# 计算每个品类的平均订单金额和最大订单
for category, stats in category_stats.items():
    if stats['valid_order_count'] > 0:
        stats['average_order_amount'] = stats['net_sales'] / stats['valid_order_count']
        # 找出最大订单
        max_order = max(stats['orders'], key=lambda x: x['adjusted_amount'])
        stats['largest_order'] = {
            'order_id': max_order['order_id'],
            'product': max_order['product'],
            'amount': max_order['adjusted_amount']
        }
    else:
        stats['average_order_amount'] = 0.0
        stats['largest_order'] = {
            'order_id': '',
            'product': '',
            'amount': 0.0
        }

# 按净销售额排序（如果相同按品类名字母序）
sorted_categories = sorted(
    category_stats.items(),
    key=lambda x: (-x[1]['net_sales'], x[0])
)

# 准备输出数据
top_categories = []
for rank, (category_name, stats) in enumerate(sorted_categories[:3], 1):
    top_categories.append({
        'rank': rank,
        'category': category_name,
        'net_sales': round(stats['net_sales'], 2),
        'valid_order_count': stats['valid_order_count'],
        'average_order_amount': round(stats['average_order_amount'], 2),
        'largest_order': {
            'order_id': stats['largest_order']['order_id'],
            'product': stats['largest_order']['product'],
            'amount': round(stats['largest_order']['amount'], 2)
        }
    })

# 被完全取消的订单（不参与统计）
dropped_orders = cancelled_order_ids

# 调整摘要
adjustment_summary = {
    'refund_order_ids': refund_order_ids,
    'cancelled_order_ids': cancelled_order_ids
}

# 摘要统计
evaluated_categories = len(category_stats)
top_category = top_categories[0]['category'] if top_categories else ''
winner_margin_vs_runner_up = 0.0
if len(top_categories) >= 2:
    winner_margin_vs_runner_up = round(top_categories[0]['net_sales'] - top_categories[1]['net_sales'], 2)

summary = {
    'evaluated_categories': evaluated_categories,
    'top_category': top_category,
    'winner_margin_vs_runner_up': winner_margin_vs_runner_up
}

# 证据引用
evidence_refs = [
    'analysis_brief.md',
    'sales_data.json',
    'adjustments.json',
    'report_contract.json'
]

# 构建最终报告
report = {
    'ranking_basis': 'net_sales_after_adjustments',
    'top_categories': top_categories,
    'dropped_orders': dropped_orders,
    'adjustment_summary': adjustment_summary,
    'summary': summary,
    'evidence_refs': evidence_refs
}

# 写入文件
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('报告已生成到 category_chain_report.json')