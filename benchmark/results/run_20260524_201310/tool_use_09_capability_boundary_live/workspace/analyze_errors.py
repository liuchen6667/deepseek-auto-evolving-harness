import json
import sys
from collections import Counter

# Files to analyze
files = ['dataset/shard_a.jsonl', 'dataset/shard_b.jsonl', 'dataset/shard_e.jsonl']

total_error_rows = 0
error_code_counts = Counter()
service_error_counts = Counter()

for file_path in files:
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if record.get('status') == 'error':
                    total_error_rows += 1
                    error_code = record.get('error_code', '')
                    if error_code:
                        error_code_counts[error_code] += 1
                    service = record.get('service', '')
                    if service:
                        service_error_counts[service] += 1
            except json.JSONDecodeError:
                continue

print(f'Total error rows: {total_error_rows}')
print(f'Error code counts: {dict(error_code_counts)}')
print(f'Service error counts: {dict(service_error_counts)}')

# Find top error code
if error_code_counts:
    top_error_code, top_error_code_count = error_code_counts.most_common(1)[0]
    print(f'Top error code: {top_error_code} ({top_error_code_count})')
else:
    top_error_code = ''
    top_error_code_count = 0

# Find top failing service
if service_error_counts:
    top_service, top_service_error_count = service_error_counts.most_common(1)[0]
    print(f'Top failing service: {top_service} ({top_service_error_count})')
else:
    top_service = ''
    top_service_error_count = 0
