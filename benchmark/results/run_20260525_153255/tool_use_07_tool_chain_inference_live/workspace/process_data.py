import json

# 读取数据
with open('sales_data.json', 'r') as f:
    sales_data = json.load(f)

with open('adjustments.json', 'r') as f:
    adjustments = json.load(f)

# 计算原始订单金额
order_details = {}
for order in sales_data:
    order_id = order['order_id']
    amount = order['quantity'] * order['unit_price']
    order_details[order_id] = {
        'category': order['category'],
        'product': order['product'],
        'original_amount': amount,
        'adjusted_amount': amount,  # 初始值
        'is_cancelled': False,
        'is_valid': True
    }

# 应用调整
refund_order_ids = []
cancelled_order_ids = []
for adj in adjustments:
    order_id = adj['order_id']
    if order_id not in order_details:
        continue
        
    if adj['type'] == 'partial_refund':
        order_details[order_id]['adjusted_amount'] += adj['amount_delta']
        refund_order_ids.append(order_id)
    elif adj['type'] == 'cancelled':
        order_details[order_id]['adjusted_amount'] = 0
        order_details[order_id]['is_cancelled'] = True
        order_details[order_id]['is_valid'] = False
        cancelled_order_ids.append(order_id)

# 按品类汇总
category_stats = {}
for order_id, details in order_details.items():
    category = details['category']
    if category not in category_stats:
        category_stats[category] = {
            'net_sales': 0.0,
            'valid_order_count': 0,
            'orders': [],  # 保存订单详情用于找最大订单
            'valid_orders': []  # 有效订单
        }
    
    # 净销售额包括所有订单（包括取消的？根据brief，取消的不计入）
    if not details['is_cancelled']:
        category_stats[category]['net_sales'] += details['adjusted_amount']
        category_stats[category]['valid_order_count'] += 1
        category_stats[category]['valid_orders'].append({
            'order_id': order_id,
            'product': details['product'],
            'adjusted_amount': details['adjusted_amount']
        })
    
    category_stats[category]['orders'].append({
        'order_id': order_id,
        'product': details['product'],
        'adjusted_amount': details['adjusted_amount'],
        'is_cancelled': details['is_cancelled']
    })

# 计算每个品类的平均订单金额和最大订单
for category, stats in category_stats.items():
    if stats['valid_order_count'] > 0:
        stats['average_order_amount'] = stats['net_sales'] / stats['valid_order_count']
        # 找最大订单（调整后金额）
        max_order = max(stats['valid_orders'], key=lambda x: x['adjusted_amount'])
        stats['largest_order'] = max_order
    else:
        stats['average_order_amount'] = 0.0
        stats['largest_order'] = None

# 按净销售额排序，如果相同按品类名字母序
sorted_categories = sorted(
    category_stats.items(),
    key=lambda x: (-x[1]['net_sales'], x[0])
)

print("Category statistics:")
for category, stats in sorted_categories:
    print(f"{category}: net_sales={stats['net_sales']:.2f}, valid_orders={stats['valid_order_count']}, avg={stats.get('average_order_amount', 0):.2f}")

print(f"\nRefund orders: {refund_order_ids}")
print(f"Cancelled orders: {cancelled_order_ids}")

# 被完全取消的订单（不参与统计）
dropped_orders = cancelled_order_ids

# 构建最终报告
top_categories_list = []
for rank, (category, stats) in enumerate(sorted_categories[:3], 1):
    top_categories_list.append({
        "rank": rank,
        "category": category,
        "net_sales": round(stats['net_sales'], 2),
        "valid_order_count": stats['valid_order_count'],
        "average_order_amount": round(stats.get('average_order_amount', 0), 2),
        "largest_order": {
            "order_id": stats['largest_order']['order_id'],
            "product": stats['largest_order']['product'],
            "amount": round(stats['largest_order']['adjusted_amount'], 2)
        } if stats['largest_order'] else {"order_id": "", "product": "", "amount": 0.0}
    })

# 计算总结
if len(sorted_categories) >= 2:
    winner_margin = sorted_categories[0][1]['net_sales'] - sorted_categories[1][1]['net_sales']
else:
    winner_margin = 0.0

summary = {
    "evaluated_categories": len(category_stats),
    "top_category": sorted_categories[0][0] if sorted_categories else "",
    "winner_margin_vs_runner_up": round(winner_margin, 2)
}

adjustment_summary = {
    "refund_order_ids": refund_order_ids,
    "cancelled_order_ids": cancelled_order_ids
}

evidence_refs = [
    "analysis_brief.md",
    "sales_data.json",
    "adjustments.json",
    "report_contract.json"
]

final_report = {
    "ranking_basis": "net_sales_after_adjustments",
    "top_categories": top_categories_list,
    "dropped_orders": dropped_orders,
    "adjustment_summary": adjustment_summary,
    "summary": summary,
    "evidence_refs": evidence_refs
}

# 输出到文件
with open('category_chain_report.json', 'w') as f:
    json.dump(final_report, f, indent=2)

print("\nReport written to category_chain_report.json")
print(f"Top categories count: {len(top_categories_list)}")