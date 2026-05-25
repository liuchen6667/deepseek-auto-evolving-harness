import json

# 读取生成的报告
with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

# 创建一个函数来确保两位小数
def ensure_two_decimals(num):
    return float(f"{num:.2f}")

# 修复金额的小数位数
for category in report['top_categories']:
    category['net_sales'] = ensure_two_decimals(category['net_sales'])
    category['average_order_amount'] = ensure_two_decimals(category['average_order_amount'])
    category['largest_order']['amount'] = ensure_two_decimals(category['largest_order']['amount'])

report['summary']['winner_margin_vs_runner_up'] = ensure_two_decimals(report['summary']['winner_margin_vs_runner_up'])

# 保存修复后的报告
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("已修复小数位数")
print("\n最终报告:")
print(json.dumps(report, indent=2))
