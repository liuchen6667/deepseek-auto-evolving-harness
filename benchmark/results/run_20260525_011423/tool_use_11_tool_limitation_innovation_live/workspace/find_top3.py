with open('aggregated_counts.txt', 'r') as f:
    agg_line = f.read().strip()

# 解析聚合计数
counts = {}
for pair in agg_line.split(','):
    key, value = pair.split('=')
    counts[key] = int(value)

# 按值排序
sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)

# 获取前3个
print("Top 3 words:")
for i, (word, count) in enumerate(sorted_items[:3], 1):
    print(f"{i}. {word}: {count}")

# 输出为列表格式
print("\nTop 3 list:")
top3 = [word for word, _ in sorted_items[:3]]
print(top3)
