#!/usr/bin/env python3
"""
数据分析脚本
读取 users.json, orders.csv, products.json
清洗数据后计算：
1. 每个用户的总消费金额（LTV）
2. 每个产品类别的销售总额
3. 每月订单数量趋势
"""

import json
import csv
import pandas as pd
from datetime import datetime
from collections import defaultdict

def read_and_clean_data():
    """读取并清洗所有数据源"""
    
    # 1. 读取用户数据
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    # 转换为字典以便快速查找
    users_dict = {user['id']: user for user in users}
    
    # 2. 读取产品数据
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    # 转换为字典以便快速查找
    products_dict = {product['id']: product for product in products}
    
    # 3. 读取订单数据并清洗
    orders = []
    seen_order_ids = set()
    
    with open('orders.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 检查订单ID是否重复
            order_id = row['order_id'].strip()
            if order_id in seen_order_ids:
                continue  # 跳过重复订单
            seen_order_ids.add(order_id)
            
            # 检查金额是否缺失或为空
            amount_str = row['amount'].strip()
            if not amount_str:
                continue  # 跳过缺失金额的订单
            
            # 转换为浮点数
            try:
                amount = float(amount_str)
            except ValueError:
                continue  # 跳过格式错误的金额
            
            # 检查用户ID是否存在
            try:
                user_id = int(row['user_id'])
            except ValueError:
                continue  # 跳过格式错误的用户ID
            
            # 检查用户是否存在
            if user_id not in users_dict:
                continue
            
            # 检查产品是否存在
            product_id = row['product'].strip()
            if product_id not in products_dict:
                continue
            
            # 处理日期，统一格式为 YYYY-MM
            date_str = row['date'].strip()
            try:
                # 尝试解析日期
                if '-' in date_str:
                    if len(date_str) == 10:  # YYYY-MM-DD 格式
                        dt = datetime.strptime(date_str, '%Y-%m-%d')
                    elif len(date_str) == 7:  # YYYY-MM 格式
                        dt = datetime.strptime(date_str + '-01', '%Y-%m-%d')
                    else:
                        continue  # 跳过格式错误的日期
                else:
                    continue  # 跳过格式错误的日期
                
                month_str = dt.strftime('%Y-%m')  # 统一格式化为 YYYY-MM
            except ValueError:
                continue  # 跳过无法解析的日期
            
            # 添加清洗后的订单
            orders.append({
                'order_id': order_id,
                'user_id': user_id,
                'product_id': product_id,
                'amount': amount,
                'month': month_str
            })
    
    return users_dict, products_dict, orders

def calculate_user_ltv(users_dict, orders):
    """计算每个用户的总消费金额（LTV）"""
    
    # 按用户ID汇总金额
    user_totals = defaultdict(float)
    user_names = {}
    
    for order in orders:
        user_id = order['user_id']
        amount = order['amount']
        
        user_totals[user_id] += amount
        if user_id not in user_names:
            user_names[user_id] = users_dict[user_id]['name']
    
    # 转换为列表并按金额降序排序
    ltv_data = []
    for user_id, total_amount in user_totals.items():
        ltv_data.append({
            'user_id': user_id,
            'name': user_names[user_id],
            'total_amount': round(total_amount, 2)
        })
    
    ltv_data.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return ltv_data

def calculate_category_sales(products_dict, orders):
    """计算每个产品类别的销售总额"""
    
    # 按产品ID获取类别
    product_to_category = {pid: p['category'] for pid, p in products_dict.items()}
    
    # 按类别汇总金额
    category_totals = defaultdict(float)
    
    for order in orders:
        product_id = order['product_id']
        amount = order['amount']
        
        category = product_to_category.get(product_id)
        if category:
            category_totals[category] += amount
    
    # 转换为字典并四舍五入
    category_sales = {category: round(total, 2) for category, total in category_totals.items()}
    
    return category_sales

def calculate_monthly_orders(orders):
    """计算每月订单数量趋势"""
    
    # 按月份计数
    monthly_counts = defaultdict(int)
    
    for order in orders:
        month = order['month']
        monthly_counts[month] += 1
    
    # 转换为列表并按月份升序排序
    monthly_data = []
    for month, count in monthly_counts.items():
        monthly_data.append({
            'month': month,
            'order_count': count
        })
    
    monthly_data.sort(key=lambda x: x['month'])
    
    return monthly_data

def write_output_files(user_ltv, category_sales, monthly_orders):
    """将结果写入输出文件"""
    
    # 1. 写入 user_ltv.csv
    with open('user_ltv.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['user_id', 'name', 'total_amount']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(user_ltv)
    
    print(f"✓ 已写入 user_ltv.csv，共 {len(user_ltv)} 条记录")
    
    # 2. 写入 category_sales.json
    with open('category_sales.json', 'w', encoding='utf-8') as f:
        json.dump(category_sales, f, indent=2)
    
    print(f"✓ 已写入 category_sales.json，共 {len(category_sales)} 个类别")
    
    # 3. 写入 monthly_orders.csv
    with open('monthly_orders.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['month', 'order_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(monthly_orders)
    
    print(f"✓ 已写入 monthly_orders.csv，共 {len(monthly_orders)} 个月份")

def main():
    """主函数"""
    print("开始数据清洗和分析...")
    
    # 读取并清洗数据
    users_dict, products_dict, orders = read_and_clean_data()
    
    print(f"✓ 数据清洗完成")
    print(f"  - 用户数: {len(users_dict)}")
    print(f"  - 产品数: {len(products_dict)}")
    print(f"  - 有效订单数: {len(orders)}")
    
    # 计算各项指标
    print("\n计算指标...")
    user_ltv = calculate_user_ltv(users_dict, orders)
    category_sales = calculate_category_sales(products_dict, orders)
    monthly_orders = calculate_monthly_orders(orders)
    
    # 写入输出文件
    print("\n写入输出文件...")
    write_output_files(user_ltv, category_sales, monthly_orders)
    
    print("\n数据分析完成！")

if __name__ == "__main__":
    main()