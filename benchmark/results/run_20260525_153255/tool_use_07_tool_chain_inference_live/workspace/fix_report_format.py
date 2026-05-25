import json

with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

# 确保所有金额字段有2位小数
for category in report['top_categories']:
    category['net_sales'] = round(float(category['net_sales']), 2)
    category['average_order_amount'] = round(float(category['average_order_amount']), 2)
    category['largest_order']['amount'] = round(float(category['largest_order']['amount']), 2)

# 确保margin有2位小数
report['summary']['winner_margin_vs_runner_up'] = round(float(report['summary']['winner_margin_vs_runner_up']), 2)

# 写回文件
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Report format fixed. Checking result:")
with open('category_chain_report.json', 'r') as f:
    fixed = json.load(f)
    
print(f"Top category margin: {fixed['summary']['winner_margin_vs_runner_up']}")
for cat in fixed['top_categories']:
    print(f"{cat['category']}: net_sales={cat['net_sales']}, avg={cat['average_order_amount']}, largest={cat['largest_order']['amount']}")