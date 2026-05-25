import json
from collections import Counter
from datetime import datetime

with open('error_log.json') as f:
    data = json.load(f)

errors = data['errors']
print(f'Total errors: {len(errors)}')

# 1. 找出出错最多的服务
services = [e['service'] for e in errors]
service_counts = Counter(services)
print('\nService counts:')
for service, count in service_counts.items():
    print(f'{service}: {count}')

most_failing_service = max(service_counts, key=service_counts.get)
print(f'\nMost failing service: {most_failing_service} ({service_counts[most_failing_service]} errors)')

# 2. 找出最常见的错误码
error_codes = [e['error_code'] for e in errors]
code_counts = Counter(error_codes)
print('\nError code counts:')
for code, count in code_counts.items():
    print(f'{code}: {count}')

most_common_error = max(code_counts, key=code_counts.get)
print(f'\nMost common error: {most_common_error} ({code_counts[most_common_error]} occurrences)')

# 3. 检查是否存在级联故障（同一分钟内 3+ 个不同服务报错）
print('\nChecking for cascade failures...')

# 按分钟分组
errors_by_minute = {}
for error in errors:
    dt = datetime.fromisoformat(error['timestamp'].replace('Z', '+00:00'))
    minute_key = dt.strftime('%Y-%m-%d %H:%M')
    if minute_key not in errors_by_minute:
        errors_by_minute[minute_key] = []
    errors_by_minute[minute_key].append(error)

cascade_detected = False
cascade_window = None

for minute, minute_errors in errors_by_minute.items():
    unique_services = set(e['service'] for e in minute_errors)
    if len(unique_services) >= 3:
        cascade_detected = True
        cascade_window = minute
        print(f'Cascade detected at {minute}: {len(unique_services)} different services failed')
        print(f'  Services: {sorted(unique_services)}')
        break

if not cascade_detected:
    print('No cascade failures detected (no minute with 3+ different services failing)')

# 输出结果
result = {
    'most_failing_service': most_failing_service,
    'most_common_error': most_common_error,
    'cascade_detected': cascade_detected,
    'cascade_window': cascade_window if cascade_detected else None,
    'total_errors': len(errors)
}

print('\nResult:')
print(json.dumps(result, indent=2))

# 保存到 diagnosis.json
with open('diagnosis.json', 'w') as f:
    json.dump(result, f, indent=2)

print('\nSaved to diagnosis.json')