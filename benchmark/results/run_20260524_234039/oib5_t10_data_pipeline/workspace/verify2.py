import csv

# 读取原始订单数据
data = list(csv.DictReader(open('orders.csv')))
print('原始订单数:', len(data))

# 正确去重和过滤
seen = set()
valid_orders = []

total_amount_by_user = {}

for row in data:
    order_id = row['order_id']
    
    # 去重
    if order_id in seen:
        print(f'跳过重复订单: {order_id}')
        continue
    seen.add(order_id)
    
    # 检查缺失金额
    if not row['amount'] or row['amount'].strip() == '':
        print(f'跳过缺失金额订单: {order_id}')
        continue
    
    valid_orders.append(row)
    
    # 计算用户总额
    user_id = int(row['user_id'])
    amount = float(row['amount'])
    total_amount_by_user[user_id] = total_amount_by_user.get(user_id, 0) + amount

print(f'有效订单数: {len(valid_orders)}')
print('用户消费总额:', dict(sorted(total_amount_by_user.items())))

# 检查每个用户的详细订单
print('\n各用户订单详情:')
for user_id in sorted(total_amount_by_user.keys()):
    user_orders = [row for row in valid_orders if int(row['user_id']) == user_id]
    print(f'用户{user_id}: {len(user_orders)}个订单, 总额: {total_amount_by_user[user_id]}')
    for order in user_orders:
        print(f'  - {order["order_id"]}: {order["product"]} = {order["amount"]}')
