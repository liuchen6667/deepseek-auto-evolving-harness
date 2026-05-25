import json
import subprocess
import os

# 获取包含 ERROR 的行数
result = subprocess.run(['grep', '-c', 'ERROR', 'logs/*.log'], 
                       capture_output=True, text=True)

# 解析结果
error_counts = {}
for line in result.stdout.strip().split('\n'):
    if ':' in line:
        filename, count = line.split(':')
        error_counts[os.path.basename(filename)] = int(count)

# 按 count 降序排序
sorted_counts = dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# 写入 JSON 文件
with open('error_summary.json', 'w') as f:
    json.dump(sorted_counts, f, indent=2)

print(f"Created error_summary.json with data: {sorted_counts}")