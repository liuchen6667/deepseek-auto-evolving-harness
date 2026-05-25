import json

# 从 team_data.json 读取数据
with open('team_data.json', 'r') as f:
    data = json.load(f)

# 获取请求的团队成员
requested_members = ['alice', 'charlie', 'dave']
scores = []

for member in data['team']:
    if member['name'] in requested_members:
        scores.append(member['performance_score'])

# 计算统计信息
scores_sorted = sorted(scores)
n = len(scores)

mean_score = sum(scores) / n if n > 0 else 0

if n % 2 == 0:
    median_score = (scores_sorted[n//2 - 1] + scores_sorted[n//2]) / 2
else:
    median_score = scores_sorted[n//2]

min_score = min(scores) if scores else 0
max_score = max(scores) if scores else 0

# 计算分数段
lt_4_0 = len([s for s in scores if s < 4.0])
gte_4_0_lt_4_5 = len([s for s in scores if 4.0 <= s < 4.5])
gte_4_5 = len([s for s in scores if s >= 4.5])

print(f"成员数量: {n}")
print(f"平均分: {mean_score:.4f}")
print(f"中位数: {median_score:.4f}")
print(f"最低分: {min_score:.4f}")
print(f"最高分: {max_score:.4f}")
print(f"分数段统计:")
print(f"  <4.0: {lt_4_0}")
print(f"  4.0-4.5: {gte_4_0_lt_4_5}")
print(f"  >=4.5: {gte_4_5}")