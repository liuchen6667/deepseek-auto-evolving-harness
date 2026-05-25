import json
import csv
import pandas as pd
from datetime import datetime
from collections import defaultdict

# 读取数据
def load_data():
    # 读取用户数据
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    # 读取产品数据
    with open('products.json', 'r') as f:
        products = json.load(f)
    
    # 读取订单数据
    orders = []
    with open('orders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(row)
    
    return users, products, orders

# 数据清洗
def clean_data(users, products, orders):
    # 1. 去重：按 order_id 去重，保留第一个出现的
    seen_ids = set()
    unique_orders = []
    for order in orders:
        order_id = order['order_id']
        if order_id not in seen_ids:
            seen_ids.add(order_id)
            unique_orders.append(order)
    
    # 2. 处理缺失值：跳过 amount 为空的订单
    cleaned_orders = []
    for order in unique_orders:
        # 检查 amount 是否存在且不为空
        amount = order.get('amount', '')
        if amount and amount.strip():
            try:
                # 确保 amount 可以转换为数字
                float(amount)
                cleaned_orders.append(order)
            except ValueError:
                continue  # 如果无法转换为数字，跳过
        
    # 3. 统一日期格式为 YYYY-MM
    for order in cleaned_orders:
        date_str = order['date']
        try:
            # 解析日期
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # 格式化为 YYYY-MM
            order['month'] = date_obj.strftime('%Y-%m')
        except ValueError:
            # 如果日期格式不正确，跳过该订单
            print(f"警告：订单 {order['order_id']} 日期格式不正确: {date_str}")
            order['month'] = None
    
    # 移除没有有效月份的订单
    cleaned_orders = [order for order in cleaned_orders if order['month']]
    
    return users, products, cleaned_orders

# 计算用户 LTV
def calculate_user_ltv(users, orders):
    # 创建用户字典以便快速查找
    user_dict = {user['id']: user for user in users}
    
    # 计算每个用户的总消费金额
    user_totals = defaultdict(float)
    for order in orders:
        user_id = int(order['user_id'])
        amount = float(order['amount'])
        user_totals[user_id] += amount
    
    # 准备输出数据
    ltv_data = []
    for user_id, total_amount in user_totals.items():
        user = user_dict.get(user_id)
        if user:
            ltv_data.append({
                'user_id': user_id,
                'name': user['name'],
                'total_amount': round(total_amount, 2)
            })
    
    # 按 total_amount 降序排序
    ltv_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return ltv_data

# 计算每个产品类别的销售总额
def calculate_category_sales(products, orders):
    # 创建产品字典以便快速查找
    product_dict = {product['id']: product for product in products}
    
    # 计算每个类别的销售总额
    category_totals = defaultdict(float)
    for order in orders:
        product_id = order['product']
        amount = float(order['amount'])
        
        product = product_dict.get(product_id)
        if product:
            category = product['category']
            category_totals[category] += amount
    
    # 转换为字典并四舍五入
    category_sales = {category: round(amount, 2) for category, amount in category_totals.items()}
    
    return category_sales

# 计算每月订单数量趋势
def calculate_monthly_orders(orders):
    # 统计每个月的订单数量
    monthly_counts = defaultdict(int)
    for order in orders:
        month = order['month']
        monthly_counts[month] += 1
    
    # 准备输出数据并按月份升序排序
    monthly_data = []
    for month in sorted(monthly_counts.keys()):
        monthly_data.append({
            'month': month,
            'order_count': monthly_counts[month]
        })
    
    return monthly_data

# 保存结果
def save_results(user_ltv, category_sales, monthly_orders):
    # 保存 user_ltv.csv
    with open('user_ltv.csv', 'w', newline='') as f:
        fieldnames = ['user_id', 'name', 'total_amount']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(user_ltv)
    
    # 保存 category_sales.json
    with open('category_sales.json', 'w') as f:
        json.dump(category_sales, f, indent=2)
    
    # 保存 monthly_orders.csv
    with open('monthly_orders.csv', 'w', newline='') as f:
        fieldnames = ['month', 'order_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(monthly_orders)

# 主函数
def main():
    print("开始数据加载...")
    users, products, orders = load_data()
    
    print("开始数据清洗...")
    users, products, cleaned_orders = clean_data(users, products, orders)
    print(f"清洗后订单数量: {len(cleaned_orders)}")
    
    print("计算用户LTV...")
    user_ltv = calculate_user_ltv(users, cleaned_orders)
    
    print("计算产品类别销售额...")
    category_sales = calculate_category_sales(products, cleaned_orders)
    
    print("计算每月订单趋势...")
    monthly_orders = calculate_monthly_orders(cleaned_orders)
    
    print("保存结果...")
    save_results(user_ltv, category_sales, monthly_orders)
    
    print("分析完成！输出文件已保存:")
    print("  - user_ltv.csv")
    print("  - category_sales.json")
    print("  - monthly_orders.csv")

if __name__ == '__main__':
    main()