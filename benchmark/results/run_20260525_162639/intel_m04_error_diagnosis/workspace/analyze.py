import json
from datetime import datetime
from collections import Counter

# 读取日志文件
with open('error_log.json', 'r') as f:
    data = json.load(f)

errors = data['errors']
print(f"Total errors: {len(errors)}")

# 1. 统计服务出错次数
service_counts = Counter(error['service'] for error in errors)
most_failing_service = service_counts.most_common(1)[0]
print(f"Service counts: {dict(service_counts)}")
print(f"Most failing service: {most_failing_service}")

# 2. 统计错误码频率
error_counts = Counter(error['error_code'] for error in errors)
most_common_error = error_counts.most_common(1)[0]
print(f"Error code counts: {dict(error_counts)}")
print(f"Most common error: {most_common_error}")

# 3. 检查级联故障（同一分钟内 3+ 个不同服务报错）
# 将时间戳解析为分钟精度的时间键
time_windows = {}
for error in errors:
    dt = datetime.fromisoformat(error['timestamp'].replace('Z', '+00:00'))
    minute_key = dt.strftime('%Y-%m-%d %H:%M')
    if minute_key not in time_windows:
        time_windows[minute_key] = set()
    time_windows[minute_key].add(error['service'])

cascade_window = None
for minute, services in time_windows.items():
    if len(services) >= 3:
        cascade_window = minute
        print(f"Cascade detected at {minute} with services: {services}")
        break

if not cascade_window:
    print("No cascade detected")

# 准备输出结果
result = {
    "most_failing_service": most_failing_service[0],
    "most_common_error": most_common_error[0],
    "cascade_detected": bool(cascade_window),
    "cascade_window": cascade_window if cascade_window else None,
    "total_errors": len(errors)
}

print(f"\nResult: {json.dumps(result, indent=2)}")

# 写入诊断文件
with open('diagnosis.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\nDiagnosis saved to diagnosis.json")