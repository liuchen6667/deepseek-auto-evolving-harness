#!/usr/bin/env python3
import json
import csv
import pandas as pd
from datetime import datetime

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

def clean_data(orders, products_dict):
    """清洗订单数据"""
    cleaned_orders = []
    seen_order_ids = set()
    
    for order in orders:
        # 1. 按order_id去重
        if order['order_id'] in seen_order_ids:
            continue
        seen_order_ids.add(order['order_id'])
        
        # 2. 跳过缺失amount的订单
        if not order['amount'] or order['amount'].strip() == '':
            continue
        
        # 3. 统一日期格式为YYYY-MM
        try:
            date_obj = datetime.strptime(order['date'], '%Y-%m-%d')
            order['month'] = date_obj.strftime('%Y-%m')
        except ValueError:
            # 如果日期格式不对，跳过
            continue
        
        # 4. 确保amount是数值
        try:
            order['amount'] = float(order['amount'])
        except ValueError:
            continue
        
        # 5. 添加产品类别信息
        product_id = order['product']
        if product_id in products_dict:
            order['category'] = products_dict[product_id]['category']
        else:
            order['category'] = 'Unknown'
        
        cleaned_orders.append(order)
    
    return cleaned_orders

def calculate_user_ltv(users, cleaned_orders):
    """计算每个用户的总消费金额"""
    # 创建用户字典
    user_dict = {user['id']: user for user in users}
    
    # 按用户汇总金额
    user_totals = {}
    for order in cleaned_orders:
        user_id = int(order['user_id'])
        amount = order['amount']
        
        if user_id not in user_totals:
            user_totals[user_id] = 0
        user_totals[user_id] += amount
    
    # 准备输出数据
    ltv_data = []
    for user_id, total_amount in user_totals.items():
        if user_id in user_dict:
            user = user_dict[user_id]
            ltv_data.append({
                'user_id': user_id,
                'name': user['name'],
                'total_amount': total_amount
            })
    
    # 按total_amount降序排序
    ltv_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return ltv_data

def calculate_category_sales(cleaned_orders):
    """计算每个产品类别的销售总额"""
    category_totals = {}
    
    for order in cleaned_orders:
        category = order['category']
        amount = order['amount']
        
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += amount
    
    return category_totals

def calculate_monthly_orders(cleaned_orders):
    """计算每月订单数量趋势"""
    monthly_counts = {}
    
    for order in cleaned_orders:
        month = order['month']
        
        if month not in monthly_counts:
            monthly_counts[month] = 0
        monthly_counts[month] += 1
    
    # 转换为列表并按月份升序排序
    monthly_data = []
    for month, count in sorted(monthly_counts.items()):
        monthly_data.append({
            'month': month,
            'order_count': count
        })
    
    return monthly_data

def write_outputs(ltv_data, category_sales, monthly_data):
    """写入输出文件"""
    
    # 1. 写入user_ltv.csv
    with open('user_ltv.csv', 'w', newline='') as f:
        fieldnames = ['user_id', 'name', 'total_amount']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in ltv_data:
            writer.writerow(row)
    
    # 2. 写入category_sales.json
    with open('category_sales.json', 'w') as f:
        json.dump(category_sales, f, indent=2)
    
    # 3. 写入monthly_orders.csv
    with open('monthly_orders.csv', 'w', newline='') as f:
        fieldnames = ['month', 'order_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in monthly_data:
            writer.writerow(row)

def main():
    print("开始数据分析...")
    
    # 加载原始数据
    users, products, orders = load_data()
    print(f"加载了 {len(users)} 个用户, {len(products)} 个产品, {len(orders)} 个订单")
    
    # 创建产品字典便于查找
    products_dict = {p['id']: p for p in products}
    
    # 清洗数据
    cleaned_orders = clean_data(orders, products_dict)
    print(f"清洗后剩余 {len(cleaned_orders)} 个有效订单")
    
    # 计算各项指标
    print("计算用户LTV...")
    ltv_data = calculate_user_ltv(users, cleaned_orders)
    
    print("计算产品类别销售额...")
    category_sales = calculate_category_sales(cleaned_orders)
    
    print("计算每月订单趋势...")
    monthly_data = calculate_monthly_orders(cleaned_orders)
    
    # 写入输出文件
    print("写入输出文件...")
    write_outputs(ltv_data, category_sales, monthly_data)
    
    print("分析完成！")
    print(f"- user_ltv.csv: {len(ltv_data)} 个用户")
    print(f"- category_sales.json: {len(category_sales)} 个类别")
    print(f"- monthly_orders.csv: {len(monthly_data)} 个月份")
    
    # 显示部分结果
    print("\n用户LTV前3名:")
    for i, user in enumerate(ltv_data[:3], 1):
        print(f"  {i}. {user['name']}: ${user['total_amount']:.2f}")
    
    print("\n产品类别销售额:")
    for category, amount in category_sales.items():
        print(f"  {category}: ${amount:.2f}")
    
    print("\n每月订单数量:")
    for month_data in monthly_data:
        print(f"  {month_data['month']}: {month_data['order_count']} 个订单")

if __name__ == '__main__':
    main()