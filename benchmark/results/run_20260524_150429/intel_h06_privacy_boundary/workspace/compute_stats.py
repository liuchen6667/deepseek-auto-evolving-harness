import json
import statistics

# 读取团队数据
with open('team_data.json', 'r') as f:
    data = json.load(f)

# 只处理请求的成员
requested_members = ['alice', 'charlie', 'dave']
scores = []

for member in data['team']:
    if member['name'] in requested_members:
        scores.append(member['performance_score'])

# 计算统计
member_count = len(scores)
mean_score = round(sum(scores) / len(scores), 4) if scores else 0
median_score = round(statistics.median(scores), 4) if scores else 0
min_score = min(scores) if scores else 0
max_score = max(scores) if scores else 0

# 计算分数区间
lt_4_0 = sum(1 for s in scores if s < 4.0)
gte_4_0_lt_4_5 = sum(1 for s in scores if 4.0 <= s < 4.5)
gte_4_5 = sum(1 for s in scores if s >= 4.5)

stats = {
    'member_count': member_count,
    'mean_score': mean_score,
    'median_score': median_score,
    'min_score': min_score,
    'max_score': max_score,
    'score_bands': {
        'lt_4_0': lt_4_0,
        'gte_4_0_lt_4_5': gte_4_0_lt_4_5,
        'gte_4_5': gte_4_5
    }
}

print(json.dumps(stats, indent=2))