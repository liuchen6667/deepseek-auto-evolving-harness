import pandas as pd
import json
from datetime import datetime

# 读取数据
def read_and_clean_data():
    """读取并清洗三个数据源"""
    
    # 1. 读取用户数据
    with open('users.json', 'r') as f:
        users_data = json.load(f)
    users_df = pd.DataFrame(users_data)
    
    # 2. 读取产品数据
    with open('products.json', 'r') as f:
        products_data = json.load(f)
    products_df = pd.DataFrame(products_data)
    
    # 3. 读取订单数据
    orders_df = pd.read_csv('orders.csv')
    
    # 数据清洗
    # 去重：按 order_id 去重
    orders_df = orders_df.drop_duplicates(subset=['order_id'], keep='first')
    
    # 处理缺失值：跳过 amount 为空的订单
    orders_df = orders_df.dropna(subset=['amount'])
    
    # 确保 amount 是数值类型
    orders_df['amount'] = pd.to_numeric(orders_df['amount'], errors='coerce')
    orders_df = orders_df.dropna(subset=['amount'])
    
    # 统一日期格式为 YYYY-MM
    orders_df['month'] = pd.to_datetime(orders_df['date']).dt.strftime('%Y-%m')
    
    return users_df, products_df, orders_df


def calculate_user_ltv(users_df, orders_df):
    """计算每个用户的总消费金额（LTV）"""
    # 按用户分组计算总消费金额
    user_spending = orders_df.groupby('user_id')['amount'].sum().reset_index()
    user_spending = user_spending.rename(columns={'amount': 'total_amount'})
    
    # 合并用户信息
    user_ltv = pd.merge(user_spending, users_df, left_on='user_id', right_on='id', how='left')
    
    # 选择需要的列并重命名
    user_ltv = user_ltv[['user_id', 'name', 'total_amount']]
    
    # 按 total_amount 降序排序
    user_ltv = user_ltv.sort_values(by='total_amount', ascending=False)
    
    # 保存到 CSV
    user_ltv.to_csv('user_ltv.csv', index=False)
    print(f"用户LTV数据已保存到 user_ltv.csv，共 {len(user_ltv)} 条记录")
    
    return user_ltv


def calculate_category_sales(orders_df, products_df):
    """计算每个产品类别的销售总额"""
    # 合并订单和产品数据
    merged_df = pd.merge(orders_df, products_df, left_on='product', right_on='id', how='left')
    
    # 按产品类别分组计算销售总额
    category_sales = merged_df.groupby('category')['amount'].sum().reset_index()
    
    # 转换为字典格式
    category_dict = dict(zip(category_sales['category'], category_sales['amount']))
    
    # 保存到 JSON
    with open('category_sales.json', 'w') as f:
        json.dump(category_dict, f, indent=2)
    
    print(f"产品类别销售数据已保存到 category_sales.json，共 {len(category_dict)} 个类别")
    
    return category_dict


def calculate_monthly_orders(orders_df):
    """计算每月订单数量趋势"""
    # 按月份分组计算订单数量
    monthly_orders = orders_df.groupby('month').size().reset_index(name='order_count')
    
    # 按月份升序排序
    monthly_orders = monthly_orders.sort_values(by='month')
    
    # 保存到 CSV
    monthly_orders.to_csv('monthly_orders.csv', index=False)
    
    print(f"月度订单趋势数据已保存到 monthly_orders.csv，共 {len(monthly_orders)} 个月份")
    
    return monthly_orders


def main():
    """主函数"""
    print("开始数据清洗和分析...")
    
    # 读取并清洗数据
    users_df, products_df, orders_df = read_and_clean_data()
    
    print(f"清洗后数据统计:")
    print(f"  - 用户数量: {len(users_df)}")
    print(f"  - 产品数量: {len(products_df)}")
    print(f"  - 有效订单数量: {len(orders_df)}")
    
    # 计算用户LTV
    print("\n计算用户LTV...")
    user_ltv = calculate_user_ltv(users_df, orders_df)
    
    # 计算产品类别销售
    print("\n计算产品类别销售总额...")
    category_sales = calculate_category_sales(orders_df, products_df)
    
    # 计算月度订单趋势
    print("\n计算月度订单趋势...")
    monthly_orders = calculate_monthly_orders(orders_df)
    
    # 输出摘要
    print("\n=== 分析完成 ===")
    print(f"用户LTV (前3名):")
    print(user_ltv.head(3).to_string(index=False))
    print(f"\n产品类别销售:")
    for category, amount in category_sales.items():
        print(f"  {category}: ${amount:.2f}")
    print(f"\n月度订单趋势:")
    print(monthly_orders.to_string(index=False))


if __name__ == "__main__":
    main()
