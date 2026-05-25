import hashlib
import json

salt = 'h06-min-disclosure-salt-v2'
names = ['alice', 'charlie', 'dave']

for name in names:
    input_str = f'{name}|{salt}'
    hash_obj = hashlib.sha256(input_str.encode())
    hex_digest = hash_obj.hexdigest()[:10]
    token = f'm_{hex_digest}'
    print(f'{name}: {token}')