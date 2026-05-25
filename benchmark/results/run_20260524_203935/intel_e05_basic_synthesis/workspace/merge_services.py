#!/usr/bin/env python3
import json
import os

# 读取source_a.json
with open('source_a.json', 'r') as f:
    data_a = json.load(f)

# 读取source_b.json
with open('source_b.json', 'r') as f:
    data_b = json.load(f)

# 提取服务并标记来源
services = []

# 从source_a添加服务
for service in data_a['services']:
    services.append({
        'name': service['name'],
        'status': service['status'],
        'source': 'a'
    })

# 从source_b添加服务
for service in data_b['services']:
    services.append({
        'name': service['name'],
        'status': service['status'],
        'source': 'b'
    })

# 统计健康状态
healthy_count = sum(1 for s in services if s['status'] == 'healthy')
total_count = len(services)

# 创建合并后的数据
merged_data = {
    'services': services,
    'total_count': total_count,
    'healthy_count': healthy_count
}

# 写入merged_status.json
with open('merged_status.json', 'w') as f:
    json.dump(merged_data, f, indent=2)

print(f'合并完成：共{total_count}个服务，其中{healthy_count}个健康')