import json
import csv
from collections import defaultdict
from datetime import datetime

print('=== 数据验证 ===')

# 读取数据
products = {p['id']: p for p in json.load(open('products.json'))}
orders = list(csv.DictReader(open('orders.csv')))

# 清洗订单数据
seen = set()
valid_orders = []
for row in orders:
    if row['order_id'] in seen:
        continue
    seen.add(row['order_id'])
    
    if not row['amount'] or row['amount'].strip() == '':
        continue
    
    row['amount'] = float(row['amount'])
    row['user_id'] = int(row['user_id'])
    
    # 统一日期格式
    date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
    row['month'] = date_obj.strftime('%Y-%m')
    
    valid_orders.append(row)

print(f'有效订单数: {len(valid_orders)}')

# 1. 验证用户LTV
print('\n1. 用户LTV验证:')
user_totals = defaultdict(float)
for order in valid_orders:
    user_totals[order['user_id']] += order['amount']

print('计算出的用户总额:', dict(sorted(user_totals.items())))

# 读取生成的user_ltv.csv
with open('user_ltv.csv') as f:
    reader = csv.DictReader(f)
    ltv_data = list(reader)

print('user_ltv.csv内容:')
for row in ltv_data:
    user_id = int(row['user_id'])
    total = float(row['total_amount'])
    print(f'  用户{user_id} ({row["name"]}): {total}')

# 2. 验证品类销售
print('\n2. 品类销售验证:')
category_totals = defaultdict(float)
for order in valid_orders:
    product_id = order['product']
    if product_id in products:
        category = products[product_id]['category']
        category_totals[category] += order['amount']

print('计算出的品类销售:', dict(sorted(category_totals.items())))

# 读取生成的category_sales.json
with open('category_sales.json') as f:
    cat_sales = json.load(f)

print('category_sales.json内容:', cat_sales)

# 3. 验证月度订单
print('\n3. 月度订单验证:')
month_counts = defaultdict(int)
for order in valid_orders:
    month_counts[order['month']] += 1

print('计算出的月度订单:', dict(sorted(month_counts.items())))

# 读取生成的monthly_orders.csv
with open('monthly_orders.csv') as f:
    reader = csv.DictReader(f)
    monthly_data = list(reader)

print('monthly_orders.csv内容:')
for row in monthly_data:
    print(f'  {row["month"]}: {row["order_count"]}')

print('\n=== 验证完成 ===')