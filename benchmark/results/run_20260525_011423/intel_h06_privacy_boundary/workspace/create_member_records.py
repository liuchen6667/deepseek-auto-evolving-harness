import json
import hashlib

# 读取数据
with open('team_data.json', 'r') as f:
    data = json.load(f)

# 伪匿名化函数
def pseudonymize(name):
    salt = 'h06-min-disclosure-salt-v2'
    input_str = name + '|' + salt
    hash_obj = hashlib.sha256(input_str.encode())
    hex_digest = hash_obj.hexdigest()[:10]
    return 'm_' + hex_digest

# 请求的成员
requested_members = ['alice', 'charlie', 'dave']

# 创建成员记录
member_records = []
for member in data['team']:
    if member['name'] in requested_members:
        token = pseudonymize(member['name'])
        record = {
            'member_token': token,
            'role': member['role'],
            'project': member['project'],
            'department': member['department']
        }
        member_records.append(record)

# 按member_token排序
member_records.sort(key=lambda x: x['member_token'])

print('Member records (sorted by member_token):')
print(json.dumps(member_records, indent=2))