import json

# 读取现有报告
with open('category_chain_report.json', 'r') as f:
    report = json.load(f)

# 重新构建报告，确保所有金额字段都是字符串格式，保留2位小数
def format_number(value):
    return round(value, 2)

# 格式化 top_categories
for cat in report['top_categories']:
    cat['net_sales'] = format_number(cat['net_sales'])
    cat['average_order_amount'] = format_number(cat['average_order_amount'])
    cat['largest_order']['amount'] = format_number(cat['largest_order']['amount'])

# 格式化 summary
report['summary']['winner_margin_vs_runner_up'] = format_number(
    report['summary']['winner_margin_vs_runner_up']
)

# 使用自定义序列化确保浮点数显示正确
import decimal

# 创建一个自定义的JSON编码器
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

# 写入文件，使用ensure_ascii=False和indent
with open('category_chain_report.json', 'w') as f:
    json.dump(report, f, indent=2, cls=DecimalEncoder)

print("最终格式化完成")

# 验证输出
with open('category_chain_report.json', 'r') as f:
    content = f.read()
    print("检查关键字段:")
    # 查找关键金额字段
    lines = content.split('\n')
    for line in lines:
        if 'net_sales' in line or 'average_order_amount' in line or 'amount' in line or 'winner_margin_vs_runner_up' in line:
            print(line.strip())