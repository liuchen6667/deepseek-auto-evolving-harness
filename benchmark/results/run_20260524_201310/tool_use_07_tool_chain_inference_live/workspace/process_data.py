import json
import math

# 读取销售数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

# 读取调整数据
with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 创建调整映射
adjustment_map = {}
for adj in adjustments:
    order_id = adj['order_id']
    if order_id not in adjustment_map:
        adjustment_map[order_id] = []
    adjustment_map[order_id].append(adj)

# 计算每个订单的原始金额
order_amounts = {}
for order in sales_data:
    order_id = order['order_id']
    amount = order['quantity'] * order['unit_price']
    order_amounts[order_id] = {
        'category': order['category'],
        'product': order['product'],
        'original_amount': amount,
        'adjusted_amount': amount,
        'is_cancelled': False
    }

# 应用调整
for order_id, adj_list in adjustment_map.items():
    if order_id not in order_amounts:
        continue
    
    for adj in adj_list:
        if adj['type'] == 'cancelled':
            order_amounts[order_id]['is_cancelled'] = True
            order_amounts[order_id]['adjusted_amount'] = 0
        elif adj['type'] == 'partial_refund':
            order_amounts[order_id]['adjusted_amount'] += adj['amount_delta']

# 按品类汇总
category_stats = {}
for order_id, data in order_amounts.items():
    category = data['category']
    if category not in category_stats:
        category_stats[category] = {
            'net_sales': 0.0,
            'valid_order_count': 0,
            'orders': [],
            'largest_order': None
        }
    
    # 如果订单被取消，不参与统计
    if data['is_cancelled']:
        continue
    
    # 添加到品类统计
    adjusted_amount = data['adjusted_amount']
    category_stats[category]['net_sales'] += adjusted_amount
    category_stats[category]['valid_order_count'] += 1
    
    order_info = {
        'order_id': order_id,
        'product': data['product'],
        'adjusted_amount': adjusted_amount
    }
    category_stats[category]['orders'].append(order_info)
    
    # 更新最大订单
    current_largest = category_stats[category]['largest_order']
    if current_largest is None or adjusted_amount > current_largest['adjusted_amount']:
        category_stats[category]['largest_order'] = order_info

# 排序：按净销售额降序，如果相同按品类名字母序升序
sorted_categories = sorted(
    category_stats.items(),
    key=lambda x: (-x[1]['net_sales'], x[0])
)

# 获取前3个品类
top_3 = sorted_categories[:3]

# 准备输出
top_categories_list = []
for i, (category, stats) in enumerate(top_3, 1):
    largest = stats['largest_order']
    avg_order = stats['net_sales'] / stats['valid_order_count'] if stats['valid_order_count'] > 0 else 0
    
    top_categories_list.append({
        'rank': i,
        'category': category,
        'net_sales': float(f"{stats['net_sales']:.2f}"),
        'valid_order_count': stats['valid_order_count'],
        'average_order_amount': float(f"{avg_order:.2f}"),
        'largest_order': {
            'order_id': largest['order_id'],
            'product': largest['product'],
            'amount': float(f"{largest['adjusted_amount']:.2f}")
        }
    })

# 获取被取消的订单（完全取消）
dropped_orders = []
for order_id, data in order_amounts.items():
    if data['is_cancelled']:
        dropped_orders.append(order_id)

# 调整汇总
refund_order_ids = []
cancelled_order_ids = []
for adj in adjustments:
    if adj['type'] == 'partial_refund':
        refund_order_ids.append(adj['order_id'])
    elif adj['type'] == 'cancelled':
        cancelled_order_ids.append(adj['order_id'])

# 计算总结
all_categories = list(category_stats.keys())
evaluated_categories = len(all_categories)
top_category = top_categories_list[0]['category'] if top_categories_list else ''
winner_margin = 0.0
if len(top_categories_list) >= 2:
    winner_margin = top_categories_list[0]['net_sales'] - top_categories_list[1]['net_sales']

# 创建最终报告
report = {
    'ranking_basis': 'net_sales_after_adjustments',
    'top_categories': top_categories_list,
    'dropped_orders': dropped_orders,
    'adjustment_summary': {
        'refund_order_ids': refund_order_ids,
        'cancelled_order_ids': cancelled_order_ids
    },
    'summary': {
        'evaluated_categories': evaluated_categories,
        'top_category': top_category,
        'winner_margin_vs_runner_up': float(f"{winner_margin:.2f}")
    },
    'evidence_refs': [
        'sales_data.json',
        'adjustments.json',
        'analysis_brief.md',
        'report_contract.json'
    ]
}

# 输出到文件
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('报告已生成到 category_chain_report.json')
print(f'评估的品类数量: {evaluated_categories}')
print(f'被取消的订单: {dropped_orders}')
print('前3品类:')
for item in top_categories_list:
    print(f"  {item['rank']}. {item['category']}: 净销售额 {item['net_sales']}")