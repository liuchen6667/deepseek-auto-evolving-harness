import json
import os
import glob

# 查找所有 .log 文件
log_files = glob.glob('logs/*.log')

error_counts = {}

for log_file in log_files:
    count = 0
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if 'ERROR' in line:
                    count += 1
    except Exception as e:
        print(f"Error reading {log_file}: {e}")
        continue
    
    filename = os.path.basename(log_file)
    error_counts[filename] = count

# 按 count 降序排序
sorted_counts = dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))

# 写入 JSON 文件
with open('error_summary.json', 'w') as f:
    json.dump(sorted_counts, f, indent=2)

print("error_summary.json created successfully!")
print("Contents:")
print(json.dumps(sorted_counts, indent=2))