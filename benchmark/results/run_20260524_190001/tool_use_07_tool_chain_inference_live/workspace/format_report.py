import json

# 读取现有报告
with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

# 辅助函数：确保浮点数保留2位小数
def format_float(value):
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    return value

# 格式化 top_categories
for cat in report['top_categories']:
    cat['net_sales'] = format_float(cat['net_sales'])
    cat['average_order_amount'] = format_float(cat['average_order_amount'])
    cat['largest_order']['amount'] = format_float(cat['largest_order']['amount'])

# 格式化 summary
report['summary']['winner_margin_vs_runner_up'] = format_float(
    report['summary']['winner_margin_vs_runner_up']
)

# 写入格式化后的报告
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("报告已重新格式化，确保所有金额保留2位小数")
print("验证格式化结果:")
with open('category_chain_report.json', 'r') as f:
    formatted = json.load(f)
    
print(f"Electronics net_sales: {formatted['top_categories'][0]['net_sales']}")
print(f"Clothing net_sales: {formatted['top_categories'][1]['net_sales']}")
print(f"Home net_sales: {formatted['top_categories'][2]['net_sales']}")
print(f"Winner margin: {formatted['summary']['winner_margin_vs_runner_up']}")