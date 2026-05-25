import pandas as pd
import json
import os

# 读取 CSV 文件
df = pd.read_csv('data.csv')

# 计算每个产品的总销售额
total_sales = df.groupby('product')['amount'].sum().sort_values(ascending=False)

# 转换为字典
result_dict = total_sales.to_dict()

# 确保输出目录存在
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 写入 JSON 文件
output_path = os.path.join(output_dir, 'result.json')
with open(output_path, 'w') as f:
    json.dump(result_dict, f, indent=2)

print(f"结果已保存到 {output_path}")
print("总销售额:")
for product, amount in result_dict.items():
    print(f"  {product}: {amount}")