#!/usr/bin/env python3
"""
数据分析脚本
读取三个数据源，清洗后计算：
1. 每个用户的总消费金额（LTV）
2. 每个产品类别的销售总额
3. 每月订单数量趋势
"""

import json
import csv
import pandas as pd
from datetime import datetime

def load_and_clean_data():
    """加载并清洗数据"""
    # 1. 加载用户数据
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    # 2. 加载产品数据
    with open('products.json', 'r') as f:
        products = json.load(f)
    
    # 3. 加载订单数据
    orders_df = pd.read_csv('orders.csv')
    
    # 数据清洗
    # a. 去重：按 order_id 去重（保留第一个出现的）
    orders_df = orders_df.drop_duplicates(subset=['order_id'], keep='first')
    
    # b. 处理缺失值：跳过 amount 为空的订单
    orders_df = orders_df.dropna(subset=['amount'])
    
    # c. 确保 amount 是数值类型
    orders_df['amount'] = pd.to_numeric(orders_df['amount'], errors='coerce')
    orders_df = orders_df.dropna(subset=['amount'])
    
    # d. 统一日期格式为 YYYY-MM
    # 先确保日期是字符串类型
    orders_df['date'] = orders_df['date'].astype(str)
    # 提取 YYYY-MM 格式
    orders_df['month'] = orders_df['date'].apply(lambda x: x[:7] if len(x) >= 7 else None)
    orders_df = orders_df.dropna(subset=['month'])
    
    return users, products, orders_df

def calculate_user_ltv(users, orders_df):
    """计算每个用户的总消费金额（LTV）"""
    # 按用户分组计算总金额
    user_spending = orders_df.groupby('user_id')['amount'].sum().reset_index()
    user_spending.columns = ['user_id', 'total_amount']
    
    # 添加用户姓名
    user_dict = {user['id']: user['name'] for user in users}
    user_spending['name'] = user_spending['user_id'].map(user_dict)
    
    # 按 total_amount 降序排序
    user_spending = user_spending.sort_values('total_amount', ascending=False)
    
    # 保存到 CSV
    user_spending.to_csv('user_ltv.csv', index=False, columns=['user_id', 'name', 'total_amount'])
    
    return user_spending

def calculate_category_sales(products, orders_df):
    """计算每个产品类别的销售总额"""
    # 创建产品ID到类别的映射
    product_to_category = {product['id']: product['category'] for product in products}
    
    # 添加类别信息到订单数据
    orders_df['category'] = orders_df['product'].map(product_to_category)
    
    # 按类别分组计算总销售额
    category_sales = orders_df.groupby('category')['amount'].sum().reset_index()
    
    # 转换为字典格式
    category_dict = dict(zip(category_sales['category'], category_sales['amount']))
    
    # 保存到 JSON
    with open('category_sales.json', 'w') as f:
        json.dump(category_dict, f, indent=2)
    
    return category_dict

def calculate_monthly_orders(orders_df):
    """计算每月订单数量趋势"""
    # 按月份分组计算订单数量
    monthly_orders = orders_df.groupby('month').size().reset_index()
    monthly_orders.columns = ['month', 'order_count']
    
    # 按月份升序排序
    monthly_orders = monthly_orders.sort_values('month')
    
    # 保存到 CSV
    monthly_orders.to_csv('monthly_orders.csv', index=False)
    
    return monthly_orders

def main():
    """主函数"""
    print("开始加载和清洗数据...")
    users, products, orders_df = load_and_clean_data()
    
    print(f"清洗后数据统计:")
    print(f"  - 用户数量: {len(users)}")
    print(f"  - 产品数量: {len(products)}")
    print(f"  - 有效订单数量: {len(orders_df)}")
    
    print("\n计算用户LTV...")
    user_ltv = calculate_user_ltv(users, orders_df)
    print(f"  - 已保存到 user_ltv.csv")
    
    print("\n计算产品类别销售额...")
    category_sales = calculate_category_sales(products, orders_df)
    print(f"  - 已保存到 category_sales.json")
    
    print("\n计算每月订单趋势...")
    monthly_orders = calculate_monthly_orders(orders_df)
    print(f"  - 已保存到 monthly_orders.csv")
    
    print("\n分析完成!")
    print("\n用户LTV预览:")
    print(user_ltv.head())
    print("\n类别销售额:")
    for category, amount in category_sales.items():
        print(f"  {category}: {amount:.2f}")
    print("\n每月订单趋势:")
    print(monthly_orders)

if __name__ == '__main__':
    main()
