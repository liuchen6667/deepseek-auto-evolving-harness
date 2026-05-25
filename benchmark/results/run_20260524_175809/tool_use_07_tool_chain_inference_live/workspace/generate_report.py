import json
import math

# 读取数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

with open('report_contract.json', 'r') as f:
    contract = json.load(f)

with open('analysis_brief.md', 'r') as f:
    analysis_brief = f.read()

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

# 获取前3个品类
top_3 = sorted_categories[:3]

# 构建top_categories列表
top_categories_list = []
for rank, (category, stats) in enumerate(top_3, 1):
    largest = stats['largest_order']
    
    category_info = {
        "rank": rank,
        "category": category,
        "net_sales": round(stats['net_sales'], 2),
        "valid_order_count": stats['valid_order_count'],
        "average_order_amount": round(stats['average_order_amount'], 2),
        "largest_order": {
            "order_id": largest['order_id'] if largest else "",
            "product": largest['product'] if largest else "",
            "amount": round(largest['adjusted_amount'], 2) if largest else 0.0
        }
    }
    top_categories_list.append(category_info)

# 计算总结数据
evaluated_categories = len(category_stats)
top_category = top_3[0][0] if top_3 else ""
if len(top_3) >= 2:
    winner_margin_vs_runner_up = round(top_3[0][1]['net_sales'] - top_3[1][1]['net_sales'], 2)
else:
    winner_margin_vs_runner_up = 0.0

# 构建最终报告
report = {
    "ranking_basis": contract["ranking_basis"],
    "top_categories": top_categories_list,
    "dropped_orders": cancelled_order_ids,  # 只列出被完全取消的订单
    "adjustment_summary": {
        "refund_order_ids": refund_order_ids,
        "cancelled_order_ids": cancelled_order_ids
    },
    "summary": {
        "evaluated_categories": evaluated_categories,
        "top_category": top_category,
        "winner_margin_vs_runner_up": winner_margin_vs_runner_up
    },
    "evidence_refs": [
        "sales_data.json",
        "adjustments.json",
        "report_contract.json",
        "analysis_brief.md"
    ]
}

# 保存报告
output_file = contract["output_file"]
with open(output_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"报告已生成: {output_file}")
print("\n报告内容预览:")
print(json.dumps(report, indent=2))
