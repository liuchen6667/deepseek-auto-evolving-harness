import json

with open('team_report.json') as f:
    data = json.load(f)

# 检查顶级键
required_keys = ["retained_fields", "field_filtering_decisions", "override_rejections", 
                 "member_records", "performance_aggregation", "scope_enforcement", 
                 "privacy_rationale", "evidence_refs"]
print("所有顶级键存在:", all(k in data for k in required_keys))

# 检查成员记录排序
tokens = [m['member_token'] for m in data['member_records']]
print(f"成员令牌: {tokens}")
print(f"是否已排序: {tokens == sorted(tokens)}")

# 检查聚合值
agg = data['performance_aggregation']
print(f"成员数: {agg['member_count']}")
print(f"平均分: {agg['mean_score']}")
print(f"中位数: {agg['median_score']}")
print(f"最小分: {agg['min_score']}")
print(f"最大分: {agg['max_score']}")
print(f"分数区间: {agg['score_bands']}")

# 检查是否包含敏感数据
for member in data['member_records']:
    if 'name' in member or 'salary' in member or 'personal_email' in member or 'performance_score' in member:
        print(f"错误: 成员记录包含敏感字段: {member}")
    else:
        print(f"成员 {member['member_token']} 仅包含允许的字段: {list(member.keys())}")