import json
from collections import Counter
from datetime import datetime

def analyze_errors():
    with open('error_log.json', 'r') as f:
        data = json.load(f)
    
    errors = data['errors']
    
    # 1. 统计服务错误
    service_counter = Counter([err['service'] for err in errors])
    most_failing_service = service_counter.most_common(1)[0][0]
    
    # 2. 统计错误码
    error_code_counter = Counter([err['error_code'] for err in errors])
    most_common_error = error_code_counter.most_common(1)[0][0]
    
    # 3. 检查级联故障
    # 按分钟分组
    minute_groups = {}
    for err in errors:
        dt = datetime.fromisoformat(err['timestamp'].replace('Z', '+00:00'))
        minute_key = dt.strftime('%Y-%m-%d %H:%M')
        if minute_key not in minute_groups:
            minute_groups[minute_key] = set()
        minute_groups[minute_key].add(err['service'])
    
    cascade_detected = False
    cascade_window = None
    for minute, services in minute_groups.items():
        if len(services) >= 3:
            cascade_detected = True
            cascade_window = minute
            break
    
    # 创建结果
    result = {
        "most_failing_service": most_failing_service,
        "most_common_error": most_common_error,
        "cascade_detected": cascade_detected,
        "cascade_window": cascade_window if cascade_detected else None,
        "total_errors": len(errors)
    }
    
    print("Analysis Results:")
    print(f"1. Most failing service: {most_failing_service} ({service_counter[most_failing_service]} errors)")
    print(f"2. Most common error code: {most_common_error} ({error_code_counter[most_common_error]} occurrences)")
    print(f"3. Cascade detected: {cascade_detected}")
    if cascade_detected:
        print(f"   Cascade window: {cascade_window}")
    print(f"4. Total errors: {len(errors)}")
    
    # 保存结果
    with open('diagnosis.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\nResults saved to diagnosis.json")

if __name__ == "__main__":
    analyze_errors()