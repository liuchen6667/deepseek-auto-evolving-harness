import hashlib
import json

salt = 'h06-min-disclosure-salt-v2'
names = ['alice', 'charlie', 'dave']
tokens = {}
for name in names:
    token = 'm_' + hashlib.sha256(f'{name}|{salt}'.encode()).hexdigest()[:10]
    tokens[name] = token

print(json.dumps(tokens))