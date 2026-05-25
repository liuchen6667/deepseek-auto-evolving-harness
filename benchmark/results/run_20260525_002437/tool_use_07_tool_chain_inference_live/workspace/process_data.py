import json
import os
from collections import defaultdict

# 读取数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

with open('report_contract.json', 'r') as f:
    report_contract = json.load(f)

# 将调整按order_id分组
adjustments_dict = {}
for adj in adjustments:
    order_id = adj['order_id']
    if order_id not in adjustments_dict:
        adjustments_dict[order_id] = []
    adjustments_dict[order_id].append(adj)

# 计算每个订单的原始金额和调整后金额
order_details = {}
cancelled_orders = set()
partial_refund_orders = set()

for order in sales_data:
    order_id = order['order_id']
    original_amount = order['quantity'] * order['unit_price']
    
    # 初始化订单详情
    order_details[order_id] = {
        'order_id': order_id,
        'category': order['category'],
        'product': order['product'],
        'original_amount': original_amount,
        'adjusted_amount': original_amount,
        'is_cancelled': False
    }

# 应用调整
for order_id, adj_list in adjustments_dict.items():
    if order_id not in order_details:
        continue
        
    for adj in adj_list:
        if adj['type'] == 'cancelled':
            order_details[order_id]['is_cancelled'] = True
            cancelled_orders.add(order_id)
        elif adj['type'] == 'partial_refund':
            order_details[order_id]['adjusted_amount'] += adj['amount_delta']
            partial_refund_orders.add(order_id)

# 按品类聚合数据
category_stats = defaultdict(lambda: {
    'net_sales': 0.0,
    'valid_order_count': 0,
    'orders': [],
    'largest_order': None
})

for order_id, details in order_details.items():
    category = details['category']
    
    if details['is_cancelled']:
        continue  # 取消的订单不计入
    
    # 更新品类统计
    category_stats[category]['net_sales'] += details['adjusted_amount']
    category_stats[category]['valid_order_count'] += 1
    category_stats[category]['orders'].append(details)
    
    # 更新最大订单
    current_largest = category_stats[category]['largest_order']
    if current_largest is None or details['adjusted_amount'] > current_largest['adjusted_amount']:
        category_stats[category]['largest_order'] = details

# 准备排序
category_list = []
for category, stats in category_stats.items():
    avg_order_amount = stats['net_sales'] / stats['valid_order_count'] if stats['valid_order_count'] > 0 else 0
    
    category_list.append({
        'category': category,
        'net_sales': round(stats['net_sales'], 2),
        'valid_order_count': stats['valid_order_count'],
        'average_order_amount': round(avg_order_amount, 2),
        'largest_order': {
            'order_id': stats['largest_order']['order_id'],
            'product': stats['largest_order']['product'],
            'amount': round(stats['largest_order']['adjusted_amount'], 2)
        } if stats['largest_order'] else None
    })

# 排序：按净销售额降序，如果相同按品类名升序
category_list.sort(key=lambda x: (-x['net_sales'], x['category']))

# 取前3个品类
top_categories = category_list[:3]

# 为前3个品类添加排名
for i, cat in enumerate(top_categories, 1):
    cat['rank'] = i

# 准备调整摘要
refund_order_ids = sorted(list(partial_refund_orders))
cancelled_order_ids = sorted(list(cancelled_orders))

# 准备summary
if len(top_categories) >= 2:
    winner_margin = top_categories[0]['net_sales'] - top_categories[1]['net_sales']
else:
    winner_margin = 0.0

summary = {
    'evaluated_categories': len(category_stats),
    'top_category': top_categories[0]['category'] if top_categories else None,
    'winner_margin_vs_runner_up': round(winner_margin, 2)
}

# 构建最终报告
report = {
    'ranking_basis': report_contract['ranking_basis'],
    'top_categories': top_categories,
    'dropped_orders': cancelled_order_ids,  # 只包含完全取消的订单
    'adjustment_summary': {
        'refund_order_ids': refund_order_ids,
        'cancelled_order_ids': cancelled_order_ids
    },
    'summary': summary,
    'evidence_refs': [
        'sales_data.json',
        'adjustments.json',
        'report_contract.json',
        'analysis_brief.md'
    ]
}

# 写入文件
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("报告已生成: category_chain_report.json")
print(f"评估的品类数量: {summary['evaluated_categories']}")
print(f"前3品类: {[cat['category'] for cat in top_categories]}")