import csv

# 读取原始订单数据
data = list(csv.DictReader(open('orders.csv')))
print('原始订单数:', len(data))

# 分析数据
seen = set()
duplicates = []
missing_amount = []

for row in data:
    if row['order_id'] in seen:
        duplicates.append(row['order_id'])
    seen.add(row['order_id'])
    
    if not row['amount'] or row['amount'].strip() == '':
        missing_amount.append(row['order_id'])

print('重复订单ID:', duplicates)
print('缺失金额订单ID:', missing_amount)
print('有效订单数:', len(data) - len(duplicates) - len(missing_amount))

# 验证用户LTV计算
print('\n验证用户消费总额:')
user_totals = {}
for row in data:
    if row['order_id'] in duplicates:
        continue
    if not row['amount'] or row['amount'].strip() == '':
        continue
    
    user_id = int(row['user_id'])
    amount = float(row['amount'])
    user_totals[user_id] = user_totals.get(user_id, 0) + amount

print('用户消费总额:', dict(sorted(user_totals.items())))