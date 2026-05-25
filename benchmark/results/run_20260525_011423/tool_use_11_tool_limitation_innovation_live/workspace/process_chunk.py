import sys

# 读取聚合文件
with open('aggregated_counts.txt', 'r') as f:
    agg_line = f.read().strip()

# 解析聚合计数
agg_dict = {}
for pair in agg_line.split(','):
    key, value = pair.split('=')
    agg_dict[key] = int(value)

# 读取分片文件
chunk_file = sys.argv[1]
with open(chunk_file, 'r') as f:
    chunk_line = f.read().strip()

# 解析分片计数
for pair in chunk_line.split(','):
    key, value = pair.split('=')
    agg_dict[key] = agg_dict.get(key, 0) + int(value)

# 写回聚合文件
result_pairs = []
for key in ['error', 'user', 'order', 'token', 'retry', 'payment']:
    result_pairs.append(f'{key}={agg_dict.get(key, 0)}')

with open('aggregated_counts.txt', 'w') as f:
    f.write(','.join(result_pairs))
