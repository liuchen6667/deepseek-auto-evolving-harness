#!/usr/bin/env python3
"""
数据分析脚本
读取 users.json, orders.csv, products.json
清洗数据并计算：
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
        users_data = json.load(f)
    
    # 转换为DataFrame
    users_df = pd.DataFrame(users_data)
    
    # 2. 加载订单数据
    orders_df = pd.read_csv('orders.csv')
    
    # 数据清洗：
    # a. 按order_id去重（保留第一条）
    orders_df = orders_df.drop_duplicates(subset=['order_id'], keep='first')
    
    # b. 删除amount为NaN或空值的行
    orders_df = orders_df.dropna(subset=['amount'])
    
    # c. 确保amount是数值类型
    orders_df['amount'] = pd.to_numeric(orders_df['amount'], errors='coerce')
    orders_df = orders_df.dropna(subset=['amount'])
    
    # d. 统一日期格式为YYYY-MM
    orders_df['month'] = pd.to_datetime(orders_df['date'], errors='coerce').dt.strftime('%Y-%m')
    orders_df = orders_df.dropna(subset=['month'])
    
    # 3. 加载产品数据
    with open('products.json', 'r') as f:
        products_data = json.load(f)
    
    products_df = pd.DataFrame(products_data)
    
    return users_df, orders_df, products_df


def calculate_user_ltv(users_df, orders_df):
    """计算每个用户的总消费金额（LTV）"""
    # 按user_id分组计算总金额
    ltv_df = orders_df.groupby('user_id')['amount'].sum().reset_index()
    ltv_df = ltv_df.rename(columns={'amount': 'total_amount'})
    
    # 合并用户信息
    ltv_df = pd.merge(ltv_df, users_df[['id', 'name']], 
                      left_on='user_id', right_on='id', how='left')
    
    # 重命名列并排序
    ltv_df = ltv_df[['user_id', 'name', 'total_amount']]
    ltv_df = ltv_df.sort_values('total_amount', ascending=False)
    
    return ltv_df


def calculate_category_sales(orders_df, products_df):
    """计算每个产品类别的销售总额"""
    # 合并订单和产品数据
    merged_df = pd.merge(orders_df, products_df, 
                        left_on='product', right_on='id', how='left')
    
    # 按类别分组计算总金额
    category_sales = merged_df.groupby('category')['amount'].sum().reset_index()
    
    # 转换为字典格式
    category_dict = dict(zip(category_sales['category'], category_sales['amount']))
    
    return category_dict


def calculate_monthly_orders(orders_df):
    """计算每月订单数量趋势"""
    # 按月份分组计数
    monthly_df = orders_df.groupby('month').size().reset_index()
    monthly_df.columns = ['month', 'order_count']
    
    # 按月份升序排序
    monthly_df = monthly_df.sort_values('month')
    
    return monthly_df


def main():
    print("开始数据加载和清洗...")
    users_df, orders_df, products_df = load_and_clean_data()
    
    print(f"清洗后用户数: {len(users_df)}")
    print(f"清洗后订单数: {len(orders_df)}")
    print(f"产品数: {len(products_df)}")
    
    # 1. 计算用户LTV
    print("\n计算用户LTV...")
    ltv_df = calculate_user_ltv(users_df, orders_df)
    
    # 输出到CSV
    ltv_df.to_csv('user_ltv.csv', index=False)
    print(f"已保存 user_ltv.csv，共 {len(ltv_df)} 个用户")
    
    # 2. 计算类别销售额
    print("\n计算产品类别销售额...")
    category_sales = calculate_category_sales(orders_df, products_df)
    
    # 输出到JSON
    with open('category_sales.json', 'w') as f:
        json.dump(category_sales, f, indent=2)
    print(f"已保存 category_sales.json，共 {len(category_sales)} 个类别")
    
    # 3. 计算月度订单趋势
    print("\n计算月度订单趋势...")
    monthly_df = calculate_monthly_orders(orders_df)
    
    # 输出到CSV
    monthly_df.to_csv('monthly_orders.csv', index=False)
    print(f"已保存 monthly_orders.csv，共 {len(monthly_df)} 个月份")
    
    print("\n分析完成！")
    
    # 打印结果摘要
    print("\n=== 结果摘要 ===")
    print("\n用户LTV（前5名）:")
    print(ltv_df.head().to_string(index=False))
    
    print("\n产品类别销售额:")
    for category, amount in category_sales.items():
        print(f"  {category}: {amount:.2f}")
    
    print("\n月度订单趋势:")
    print(monthly_df.to_string(index=False))


if __name__ == '__main__':
    main()
