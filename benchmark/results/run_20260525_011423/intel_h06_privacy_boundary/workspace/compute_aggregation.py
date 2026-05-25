import json
import statistics

# 读取team_data.json
with open('team_data.json', 'r') as f:
    data = json.load(f)

# 请求的成员
requested_members = ['alice', 'charlie', 'dave']

# 提取绩效分数
scores = []
for member in data['team']:
    if member['name'] in requested_members:
        scores.append(member['performance_score'])

print(f'Scores: {scores}')
print(f'Member count: {len(scores)}')
print(f'Mean: {statistics.mean(scores) if scores else 0:.4f}')
print(f'Median: {statistics.median(scores) if scores else 0:.4f}')
print(f'Min: {min(scores) if scores else 0:.4f}')
print(f'Max: {max(scores) if scores else 0:.4f}')

# 计算分数区间
lt_4_0 = sum(1 for s in scores if s < 4.0)
gte_4_0_lt_4_5 = sum(1 for s in scores if 4.0 <= s < 4.5)
gte_4_5 = sum(1 for s in scores if s >= 4.5)

print(f'lt_4_0: {lt_4_0}')
print(f'gte_4_0_lt_4_5: {gte_4_0_lt_4_5}')
print(f'gte_4_5: {gte_4_5}')