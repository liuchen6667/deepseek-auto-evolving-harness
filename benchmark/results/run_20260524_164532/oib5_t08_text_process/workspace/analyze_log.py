#!/usr/bin/env python3
import json
import re
from collections import Counter, defaultdict

def parse_log_line(line):
    """解析单行日志，返回字典包含ip和status_code"""
    # 使用正则表达式匹配IP地址和状态码
    # 格式示例: 192.168.1.100 - - [10/Oct/2000:13:55:01 -0700] "GET /index.html HTTP/1.1" 200 2326
    pattern = r'^(\S+) .* \"[^\"]+\" (\d{3})'
    match = re.match(pattern, line)
    if match:
        return {
            'ip': match.group(1),
            'status_code': match.group(2),
            'full_line': line.strip()
        }
    return None

def analyze_log_file(log_file_path):
    """分析日志文件并生成报告"""
    with open(log_file_path, 'r') as f:
        lines = f.readlines()
    
    total_requests = len(lines)
    status_codes = Counter()
    ip_counts = Counter()
    error_requests = []
    
    for line in lines:
        parsed = parse_log_line(line)
        if parsed:
            ip = parsed['ip']
            status_code = parsed['status_code']
            
            # 统计状态码
            status_codes[status_code] += 1
            
            # 统计IP请求数
            ip_counts[ip] += 1
            
            # 收集错误请求（状态码>=400）
            if int(status_code) >= 400:
                error_requests.append(parsed['full_line'])
    
    # 准备top_ips数据
    top_ips = [{'ip': ip, 'count': count} for ip, count in ip_counts.most_common()]
    
    # 准备状态码字典
    status_codes_dict = {code: count for code, count in status_codes.items()}
    
    # 构建报告
    report = {
        'total_requests': total_requests,
        'status_codes': status_codes_dict,
        'top_ips': top_ips,
        'error_requests': error_requests
    }
    
    return report

if __name__ == '__main__':
    report = analyze_log_file('access.log')
    
    # 输出JSON报告
    with open('report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"分析完成，共处理 {report['total_requests']} 条请求")
    print(f"状态码统计: {report['status_codes']}")
    print(f"错误请求数: {len(report['error_requests'])}")
