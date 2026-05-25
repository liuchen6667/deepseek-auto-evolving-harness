import hashlib
import json

salt = 'h06-min-disclosure-salt-v2'
names = ['alice', 'charlie', 'dave']
tokens = {}

for name in names:
    input_str = f'{name}|{salt}'
    hash_obj = hashlib.sha256(input_str.encode())
    token = 'm_' + hash_obj.hexdigest()[:10]
    tokens[name] = token
    print(f'{name}: {token}')

# 保存到文件以便后续使用
with open('tokens.json', 'w') as f:
    json.dump(tokens, f)