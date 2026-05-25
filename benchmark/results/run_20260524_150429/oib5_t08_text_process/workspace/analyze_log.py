#!/usr/bin/env python3
import re
import json
from collections import Counter, defaultdict

def parse_log_line(line):
    """解析单行日志，提取IP和状态码"""
    # 匹配IP地址
    ip_match = re.match(r'^(\d+\.\d+\.\d+\.\d+)', line)
    ip = ip_match.group(1) if ip_match else "unknown"
    
    # 匹配状态码
    status_match = re.search(r'"\s+(\d{3})\s+', line)
    status_code = status_match.group(1) if status_match else "000"
    
    return ip, status_code, line.strip()

def analyze_log_file(filename):
    """分析日志文件"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    total_requests = len(lines)
    status_codes = defaultdict(int)
    ip_counts = Counter()
    error_requests = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        ip, status_code, full_line = parse_log_line(line)
        
        # 统计状态码
        status_codes[status_code] += 1
        
        # 统计IP
        ip_counts[ip] += 1
        
        # 收集错误请求（状态码>=400）
        if int(status_code) >= 400:
            error_requests.append(full_line)
    
    # 生成top_ips列表
    top_ips = [{"ip": ip, "count": count} for ip, count in ip_counts.most_common()]
    
    # 构建报告
    report = {
        "total_requests": total_requests,
        "status_codes": dict(status_codes),
        "top_ips": top_ips,
        "error_requests": error_requests
    }
    
    return report

def main():
    report = analyze_log_file("access.log")
    
    # 写入report.json
    with open("report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("分析完成！报告已保存到 report.json")
    print(f"总请求数: {report['total_requests']}")
    print(f"状态码分布: {report['status_codes']}")
    print(f"错误请求数: {len(report['error_requests'])}")

if __name__ == "__main__":
    main()