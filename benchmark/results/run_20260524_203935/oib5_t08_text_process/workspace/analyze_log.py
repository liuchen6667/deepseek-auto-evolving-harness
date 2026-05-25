#!/usr/bin/env python3
import re
import json
from collections import Counter, defaultdict

def analyze_log(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    total_requests = len(lines)
    status_counter = Counter()
    ip_counter = Counter()
    error_requests = []
    
    # 正则表达式匹配日志格式：IP - - [时间] "请求" 状态码 字节数
    # 简化版：匹配IP和状态码
    ip_pattern = r'^(\S+)'
    status_pattern = r'"\s+(\d{3})\s+\d+$'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 提取IP
        ip_match = re.match(ip_pattern, line)
        if ip_match:
            ip = ip_match.group(1)
            ip_counter[ip] += 1
        
        # 提取状态码
        status_match = re.search(status_pattern, line)
        if status_match:
            status = status_match.group(1)
            status_counter[status] += 1
            
            # 检查是否为错误请求（状态码 >= 400）
            if int(status) >= 400:
                error_requests.append(line)
    
    # 准备top_ips列表，按计数降序排列
    top_ips = [{"ip": ip, "count": count} for ip, count in ip_counter.most_common()]
    
    # 准备状态码字典
    status_codes = {str(code): count for code, count in sorted(status_counter.items())}
    
    # 构建报告
    report = {
        "total_requests": total_requests,
        "status_codes": status_codes,
        "top_ips": top_ips,
        "error_requests": error_requests
    }
    
    return report

if __name__ == "__main__":
    report = analyze_log("access.log")
    
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("报告已生成到 report.json")
    print(json.dumps(report, indent=2))