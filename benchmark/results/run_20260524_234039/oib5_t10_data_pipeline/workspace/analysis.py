#!/usr/bin/env python3
import json
import csv
from collections import defaultdict
from datetime import datetime

def read_users():
    """读取用户数据"""
    with open('users.json', 'r') as f:
        return {user['id']: user for user in json.load(f)}

def read_products():
    """读取产品数据"""
    with open('products.json', 'r') as f:
        return {product['id']: product for product in json.load(f)}

def read_and_clean_orders():
    """读取并清洗订单数据"""
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
            
            # 转换数据类型
            row['amount'] = float(row['amount'])
            row['user_id'] = int(row['user_id'])
            
            # 统一日期格式为 YYYY-MM
            try:
                date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                row['month'] = date_obj.strftime('%Y-%m')
            except ValueError:
                # 如果日期格式不一致，尝试其他格式
                try:
                    date_obj = datetime.strptime(row['date'], '%Y/%m/%d')
                    row['month'] = date_obj.strftime('%Y-%m')
                except ValueError:
                    # 如果还是失败，跳过这条记录
                    continue
            
            orders.append(row)
    
    return orders

def calculate_user_ltv(users, orders):
    """计算每个用户的总消费金额（LTV）"""
    user_totals = defaultdict(float)
    
    for order in orders:
        user_id = order['user_id']
        user_totals[user_id] += order['amount']
    
    # 创建结果列表
    results = []
    for user_id, total_amount in user_totals.items():
        if user_id in users:
            user = users[user_id]
            results.append({
                'user_id': user_id,
                'name': user['name'],
                'total_amount': total_amount
            })
    
    # 按 total_amount 降序排序
    results.sort(key=lambda x: x['total_amount'], reverse=True)
    
    return results

def calculate_category_sales(orders, products):
    """计算每个产品类别的销售总额"""
    category_totals = defaultdict(float)
    
    for order in orders:
        product_id = order['product']
        if product_id in products:
            product = products[product_id]
            category = product['category']
            category_totals[category] += order['amount']
    
    # 转换为字典并排序
    result = {category: amount for category, amount in sorted(category_totals.items())}
    return result

def calculate_monthly_orders(orders):
    """计算每月订单数量趋势"""
    month_counts = defaultdict(int)
    
    for order in orders:
        month = order['month']
        month_counts[month] += 1
    
    # 创建结果列表并按月份升序排序
    results = []
    for month, order_count in sorted(month_counts.items()):
        results.append({
            'month': month,
            'order_count': order_count
        })
    
    return results

def write_user_ltv(results):
    """输出 user_ltv.csv"""
    with open('user_ltv.csv', 'w', newline='') as f:
        fieldnames = ['user_id', 'name', 'total_amount']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

def write_category_sales(results):
    """输出 category_sales.json"""
    with open('category_sales.json', 'w') as f:
        json.dump(results, f, indent=2)

def write_monthly_orders(results):
    """输出 monthly_orders.csv"""
    with open('monthly_orders.csv', 'w', newline='') as f:
        fieldnames = ['month', 'order_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

def main():
    """主函数"""
    print("读取数据...")
    users = read_users()
    products = read_products()
    orders = read_and_clean_orders()
    
    print(f"读取到 {len(users)} 个用户，{len(products)} 个产品，{len(orders)} 个有效订单")
    
    print("计算用户LTV...")
    user_ltv = calculate_user_ltv(users, orders)
    write_user_ltv(user_ltv)
    
    print("计算品类销售...")
    category_sales = calculate_category_sales(orders, products)
    write_category_sales(category_sales)
    
    print("计算月度订单趋势...")
    monthly_orders = calculate_monthly_orders(orders)
    write_monthly_orders(monthly_orders)
    
    print("完成！输出文件已生成。")
    
    # 显示统计信息
    print(f"\n统计信息：")
    print(f"- 用户LTV记录数: {len(user_ltv)}")
    print(f"- 产品类别数: {len(category_sales)}")
    print(f"- 月份数: {len(monthly_orders)}")

if __name__ == '__main__':
    main()
