import json

# 读取现有报告
with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

# 重新排序 top_categories 中的字段
for category in report['top_categories']:
    # 创建新字典，按要求的顺序
    new_category = {
        'rank': category['rank'],
        'category': category['category'],
        'net_sales': category['net_sales'],
        'valid_order_count': category['valid_order_count'],
        'average_order_amount': category['average_order_amount'],
        'largest_order': category['largest_order']
    }
    # 替换原对象
    category.clear()
    category.update(new_category)

# 写入新文件
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("字段顺序已调整")