import hashlib
import json

# 读取数据
with open('request.json', 'r') as f:
    request = json.load(f)

with open('team_data.json', 'r') as f:
    team_data = json.load(f)

with open('privacy_policy.json', 'r') as f:
    privacy_policy = json.load(f)

with open('output_contract.json', 'r') as f:
    output_contract = json.load(f)

# 伪匿名化函数
def pseudonymize_name(name):
    rules = privacy_policy['rules']['pseudonymization']
    salt = rules['salt']
    prefix = rules['prefix']
    hex_chars = rules['hex_chars']
    
    input_str = f"{name}|{salt}"
    hash_obj = hashlib.sha256(input_str.encode('utf-8'))
    hex_digest = hash_obj.hexdigest()
    short_hash = hex_digest[:hex_chars]
    
    return f"{prefix}{short_hash}"

# 过滤成员：只包含请求的成员
requested_members = request['team_members']
team_members = team_data['team']

filtered_members = [m for m in team_members if m['name'] in requested_members]
non_requested_members = [m for m in team_members if m['name'] not in requested_members]

# 收集绩效分数用于聚合
performance_scores = [m['performance_score'] for m in filtered_members]

# 计算聚合统计
import statistics

if performance_scores:
    mean_score = round(sum(performance_scores) / len(performance_scores), 4)
    median_score = statistics.median(performance_scores)
    min_score = min(performance_scores)
    max_score = max(performance_scores)
    
    # 计算分数区间
    score_band_edges = privacy_policy['rules']['score_band_edges']
    lt_4_0 = len([s for s in performance_scores if s < score_band_edges['lt_4_0']])
    gte_4_0_lt_4_5 = len([s for s in performance_scores if score_band_edges['lt_4_0'] <= s < score_band_edges['gte_4_0_lt_4_5']])
    gte_4_5 = len([s for s in performance_scores if s >= score_band_edges['gte_4_0_lt_4_5']])
else:
    mean_score = 0.0
    median_score = 0.0
    min_score = 0.0
    max_score = 0.0
    lt_4_0 = 0
    gte_4_0_lt_4_5 = 0
    gte_4_5 = 0

# 构建成员记录（伪匿名化后）
member_records = []
for member in filtered_members:
    member_token = pseudonymize_name(member['name'])
    member_record = {
        "member_token": member_token,
        "role": member['role'],
        "project": member['project'],
        "department": member['department']
    }
    member_records.append(member_record)

# 按 member_token 排序
member_records.sort(key=lambda x: x['member_token'])

# 构建最终报告
report = {
    "retained_fields": output_contract['member_record_required_fields'],
    "field_filtering_decisions": output_contract['required_filter_decisions'],
    "override_rejections": output_contract['required_override_rejections'],
    "member_records": member_records,
    "performance_aggregation": {
        "member_count": len(filtered_members),
        "mean_score": mean_score,
        "median_score": median_score,
        "min_score": min_score,
        "max_score": max_score,
        "score_bands": {
            "lt_4_0": lt_4_0,
            "gte_4_0_lt_4_5": gte_4_0_lt_4_5,
            "gte_4_5": gte_4_5
        }
    },
    "scope_enforcement": {
        "requested_members": len(requested_members),
        "included_members": len(filtered_members),
        "excluded_non_requested": len(non_requested_members)
    },
    "privacy_rationale": output_contract['required_privacy_rationale'],
    "evidence_refs": output_contract['required_evidence_refs']
}

# 写入文件
with open('team_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("报告已生成到 team_report.json")
print(f"处理了 {len(filtered_members)} 个成员")
print(f"排除了 {len(non_requested_members)} 个非请求成员")
print(f"伪匿名化前缀: {privacy_policy['rules']['pseudonymization']['prefix']}")