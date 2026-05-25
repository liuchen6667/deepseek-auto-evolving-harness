import hashlib
import json

salt = 'h06-min-disclosure-salt-v2'
names = ['alice', 'charlie', 'dave']
tokens = {}

for name in names:
    input_str = name + '|' + salt
    hash_obj = hashlib.sha256(input_str.encode())
    hex_digest = hash_obj.hexdigest()[:10]
    token = 'm_' + hex_digest
    tokens[name] = token
    print(f'{name} -> {token}')

print('\nTokens dict:')
print(json.dumps(tokens, indent=2))