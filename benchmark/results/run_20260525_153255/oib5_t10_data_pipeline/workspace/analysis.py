import json
import csv
from datetime import datetime
from collections import defaultdict

# 读取用户数据
with open('users.json', 'r') as f:
    users = json.load(f)

# 读取产品数据
with open('products.json', 'r') as f:
    products = json.load(f)

# 创建产品ID到类别的映射
product_to_category = {}
for product in products:
    product_to_category[product['id']] = product['category']

# 读取订单数据并进行清洗
orders = []
seen_order_ids = set()

with open('orders.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # 按 order_id 去重
        if row['order_id'] in seen_order_ids:
            continue
        seen_order_ids.add(row['order_id'])
        
        # 跳过缺失 amount 的订单
        if not row['amount'] or row['amount'].strip() == '':
            continue
        
        # 转换 amount 为浮点数
        try:
            amount = float(row['amount'])
        except ValueError:
            continue
        
        # 统一日期格式为 YYYY-MM
        try:
            date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
            month_str = date_obj.strftime('%Y-%m')
        except ValueError:
            # 如果日期格式不正确，跳过
            continue
        
        # 获取产品类别
        category = product_to_category.get(row['product'], 'Unknown')
        
        orders.append({
            'order_id': row['order_id'],
            'user_id': int(row['user_id']),
            'product': row['product'],
            'amount': amount,
            'date': row['date'],
            'month': month_str,
            'category': category
        })

print(f"清洗后订单数量: {len(orders)}")

# 1. 计算每个用户的总消费金额（LTV）
user_ltv = defaultdict(float)
user_info = {}
for user in users:
    user_info[user['id']] = user['name']

for order in orders:
    user_ltv[order['user_id']] += order['amount']

# 转换为列表并按 total_amount 降序排序
ltv_list = []
for user_id, total_amount in user_ltv.items():
    name = user_info.get(user_id, 'Unknown')
    ltv_list.append({
        'user_id': user_id,
        'name': name,
        'total_amount': total_amount
    })

ltv_list.sort(key=lambda x: x['total_amount'], reverse=True)

# 输出到 user_ltv.csv
with open('user_ltv.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['user_id', 'name', 'total_amount'])
    writer.writeheader()
    writer.writerows(ltv_list)

print(f"用户LTV数据已保存到 user_ltv.csv，共 {len(ltv_list)} 条记录")

# 2. 计算每个产品类别的销售总额
category_sales = defaultdict(float)
for order in orders:
    category_sales[order['category']] += order['amount']

# 转换为字典并输出到 category_sales.json
category_dict = dict(category_sales)
with open('category_sales.json', 'w') as f:
    json.dump(category_dict, f, indent=2)

print(f"类别销售数据已保存到 category_sales.json，共 {len(category_dict)} 个类别")

# 3. 计算每月订单数量趋势
monthly_orders = defaultdict(int)
for order in orders:
    monthly_orders[order['month']] += 1

# 转换为列表并按月份升序排序
monthly_list = []
for month, order_count in monthly_orders.items():
    monthly_list.append({
        'month': month,
        'order_count': order_count
    })

monthly_list.sort(key=lambda x: x['month'])

# 输出到 monthly_orders.csv
with open('monthly_orders.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['month', 'order_count'])
    writer.writeheader()
    writer.writerows(monthly_list)

print(f"月度订单趋势已保存到 monthly_orders.csv，共 {len(monthly_list)} 个月份")

print("所有分析完成！")