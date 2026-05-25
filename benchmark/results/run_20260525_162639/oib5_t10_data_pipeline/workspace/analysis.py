import pandas as pd
import json
from datetime import datetime

def load_and_clean_data():
    """加载并清洗三个数据源"""
    
    # 1. 加载用户数据
    with open('users.json', 'r') as f:
        users_data = json.load(f)
    users_df = pd.DataFrame(users_data)
    
    # 2. 加载产品数据
    with open('products.json', 'r') as f:
        products_data = json.load(f)
    products_df = pd.DataFrame(products_data)
    
    # 3. 加载订单数据
    orders_df = pd.read_csv('orders.csv')
    
    # 4. 清洗订单数据
    # 去重：按 order_id 去重，保留第一个出现
    orders_df = orders_df.drop_duplicates(subset=['order_id'], keep='first')
    
    # 处理缺失值：跳过 amount 为空的订单
    orders_df = orders_df.dropna(subset=['amount'])
    
    # 确保 amount 是数值类型
    orders_df['amount'] = pd.to_numeric(orders_df['amount'], errors='coerce')
    orders_df = orders_df.dropna(subset=['amount'])
    
    # 日期格式统一为 YYYY-MM
    # 先尝试解析日期
    orders_df['date'] = pd.to_datetime(orders_df['date'], errors='coerce')
    orders_df = orders_df.dropna(subset=['date'])
    orders_df['month'] = orders_df['date'].dt.strftime('%Y-%m')
    
    return users_df, products_df, orders_df

def calculate_user_ltv(users_df, orders_df):
    """计算每个用户的总消费金额（LTV）"""
    
    # 合并用户和订单数据
    user_orders = pd.merge(orders_df, users_df, left_on='user_id', right_on='id', how='inner')
    
    # 按用户分组计算总消费
    user_ltv = user_orders.groupby(['user_id', 'name']).agg(
        total_amount=('amount', 'sum')
    ).reset_index()
    
    # 按 total_amount 降序排序
    user_ltv = user_ltv.sort_values('total_amount', ascending=False)
    
    # 保存到 CSV
    user_ltv.to_csv('user_ltv.csv', index=False)
    print(f"用户LTV数据已保存到 user_ltv.csv，共 {len(user_ltv)} 个用户")
    
    return user_ltv

def calculate_category_sales(orders_df, products_df):
    """计算每个产品类别的销售总额"""
    
    # 合并订单和产品数据
    order_products = pd.merge(orders_df, products_df, left_on='product', right_on='id', how='inner')
    
    # 按产品类别分组计算销售总额
    category_sales = order_products.groupby('category').agg(
        total_amount=('amount', 'sum')
    ).reset_index()
    
    # 转换为字典格式
    category_dict = dict(zip(category_sales['category'], category_sales['total_amount']))
    
    # 保存到 JSON
    with open('category_sales.json', 'w') as f:
        json.dump(category_dict, f, indent=2)
    
    print(f"类别销售数据已保存到 category_sales.json，共 {len(category_dict)} 个类别")
    
    return category_dict

def calculate_monthly_orders(orders_df):
    """计算每月订单数量趋势"""
    
    # 按月份分组计算订单数量
    monthly_orders = orders_df.groupby('month').agg(
        order_count=('order_id', 'count')
    ).reset_index()
    
    # 按月份升序排序
    monthly_orders = monthly_orders.sort_values('month')
    
    # 保存到 CSV
    monthly_orders.to_csv('monthly_orders.csv', index=False)
    print(f"月度订单趋势已保存到 monthly_orders.csv，共 {len(monthly_orders)} 个月份")
    
    return monthly_orders

def main():
    """主函数"""
    print("开始数据清洗和分析...")
    
    try:
        # 1. 加载并清洗数据
        users_df, products_df, orders_df = load_and_clean_data()
        
        print(f"清洗后数据统计:")
        print(f"  - 用户数: {len(users_df)}")
        print(f"  - 产品数: {len(products_df)}")
        print(f"  - 有效订单数: {len(orders_df)}")
        
        # 2. 计算用户LTV
        user_ltv = calculate_user_ltv(users_df, orders_df)
        
        # 3. 计算类别销售额
        category_sales = calculate_category_sales(orders_df, products_df)
        
        # 4. 计算月度订单趋势
        monthly_orders = calculate_monthly_orders(orders_df)
        
        print("\n分析完成！")
        print("输出文件:")
        print("  - user_ltv.csv: 用户LTV数据")
        print("  - category_sales.json: 类别销售数据")
        print("  - monthly_orders.csv: 月度订单趋势")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()