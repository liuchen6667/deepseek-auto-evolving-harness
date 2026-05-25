import json
import csv
from collections import defaultdict
from datetime import datetime

def read_users():
    with open('users.json', 'r') as f:
        users = json.load(f)
    # 转换为字典方便查找
    return {user['id']: user for user in users}

def read_products():
    with open('products.json', 'r') as f:
        products = json.load(f)
    # 转换为字典方便查找
    return {product['id']: product for product in products}

def read_and_clean_orders():
    orders = []
    seen_order_ids = set()
    
    with open('orders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 去重：按 order_id 去重
            if row['order_id'] in seen_order_ids:
                continue
            seen_order_ids.add(row['order_id'])
            
            # 检查缺失 amount
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
                month = date_obj.strftime('%Y-%m')
            except ValueError:
                # 如果日期格式不正确，跳过
                continue
            
            orders.append({
                'order_id': row['order_id'],
                'user_id': int(row['user_id']),
                'product': row['product'],
                'amount': amount,
                'month': month
            })
    
    return orders

def calculate_user_ltv(orders, users):
    user_totals = defaultdict(float)
    user_names = {}
    
    for order in orders:
        user_id = order['user_id']
        user_totals[user_id] += order['amount']
        # 记录用户姓名
        if user_id in users:
            user_names[user_id] = users[user_id]['name']
    
    # 转换为列表并排序
    ltv_list = []
    for user_id, total in user_totals.items():
        name = user_names.get(user_id, f'User_{user_id}')
        ltv_list.append({
            'user_id': user_id,
            'name': name,
            'total_amount': round(total, 2)
        })
    
    # 按 total_amount 降序排序
    ltv_list.sort(key=lambda x: x['total_amount'], reverse=True)
    return ltv_list

def calculate_category_sales(orders, products):
    category_totals = defaultdict(float)
    
    for order in orders:
        product_id = order['product']
        if product_id in products:
            category = products[product_id]['category']
            category_totals[category] += order['amount']
    
    # 转换为字典，金额四舍五入
    result = {category: round(amount, 2) for category, amount in category_totals.items()}
    return result

def calculate_monthly_orders(orders):
    monthly_counts = defaultdict(int)
    
    for order in orders:
        month = order['month']
        monthly_counts[month] += 1
    
    # 转换为列表并排序
    monthly_list = []
    for month, count in monthly_counts.items():
        monthly_list.append({
            'month': month,
            'order_count': count
        })
    
    # 按月份升序排序
    monthly_list.sort(key=lambda x: x['month'])
    return monthly_list

def main():
    # 读取数据
    users = read_users()
    products = read_products()
    orders = read_and_clean_orders()
    
    print(f"读取用户数: {len(users)}")
    print(f"读取产品数: {len(products)}")
    print(f"清洗后订单数: {len(orders)}")
    
    # 计算用户LTV
    user_ltv = calculate_user_ltv(orders, users)
    
    # 输出 user_ltv.csv
    with open('user_ltv.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'name', 'total_amount'])
        writer.writeheader()
        writer.writerows(user_ltv)
    
    print(f"已生成 user_ltv.csv，包含 {len(user_ltv)} 条记录")
    
    # 计算品类销售总额
    category_sales = calculate_category_sales(orders, products)
    
    # 输出 category_sales.json
    with open('category_sales.json', 'w') as f:
        json.dump(category_sales, f, indent=2)
    
    print(f"已生成 category_sales.json，包含 {len(category_sales)} 个品类")
    
    # 计算月度订单趋势
    monthly_orders = calculate_monthly_orders(orders)
    
    # 输出 monthly_orders.csv
    with open('monthly_orders.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['month', 'order_count'])
        writer.writeheader()
        writer.writerows(monthly_orders)
    
    print(f"已生成 monthly_orders.csv，包含 {len(monthly_orders)} 个月份")

if __name__ == '__main__':
    main()