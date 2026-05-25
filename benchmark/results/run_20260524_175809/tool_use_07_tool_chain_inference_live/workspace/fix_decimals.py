import json

# 读取生成的报告
with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

# 修复金额的小数位数
for category in report['top_categories']:
    category['net_sales'] = round(category['net_sales'], 2)
    category['average_order_amount'] = round(category['average_order_amount'], 2)
    category['largest_order']['amount'] = round(category['largest_order']['amount'], 2)

report['summary']['winner_margin_vs_runner_up'] = round(report['summary']['winner_margin_vs_runner_up'], 2)

# 保存修复后的报告
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("已修复小数位数")
print("\n修复后的报告:")
print(json.dumps(report, indent=2))
