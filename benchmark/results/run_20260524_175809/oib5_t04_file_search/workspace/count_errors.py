#!/usr/bin/env python3
import json
import os
import glob

# 获取所有 .log 文件
log_files = glob.glob('logs/*.log')
error_counts = {}

# 统计每个文件的 ERROR 数量
for log_file in log_files:
    filename = os.path.basename(log_file)
    count = 0
    with open(log_file, 'r') as f:
        for line in f:
            if 'ERROR' in line:
                count += 1
    error_counts[filename] = count

# 按 count 降序排序
sorted_counts = dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# 写入 JSON 文件
with open('error_summary.json', 'w') as f:
    json.dump(sorted_counts, f, indent=2)

print(f"ERROR统计结果已保存到 error_summary.json")
print("统计结果:")
for filename, count in sorted_counts.items():
    print(f"  {filename}: {count}")