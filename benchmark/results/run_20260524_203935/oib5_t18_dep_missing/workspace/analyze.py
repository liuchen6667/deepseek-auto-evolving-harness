#!/usr/bin/env python
"""分析脚本 — 使用 Python 标准库 csv 模块"""
import csv
import json
import sys

def analyze_csv_with_standard_lib():
    """使用标准库 csv 模块分析 CSV 文件"""
    category_totals = {}
    
    try:
        with open("data.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            
            # 验证列是否存在
            if "category" not in reader.fieldnames:
                print("错误: CSV 文件中缺少 'category' 列")
                sys.exit(1)
            if "amount" not in reader.fieldnames:
                print("错误: CSV 文件中缺少 'amount' 列")
                sys.exit(1)
            
            for row in reader:
                category = row["category"]
                try:
                    amount = float(row["amount"])
                except ValueError:
                    print(f"警告: 行 {reader.line_num} 的 amount 值无效: {row['amount']}")
                    continue
                
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
                
    except FileNotFoundError:
        print("错误: 找不到 data.csv 文件")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取 CSV 文件时发生异常: {e}")
        sys.exit(1)
    
    return category_totals

if __name__ == "__main__":
    # 使用标准库进行分析
    result = analyze_csv_with_standard_lib()
    
    # 将结果保存到 result.json
    try:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"分析完成，结果已保存到 result.json")
        print("每个类别的金额总和:")
        for category, total in sorted(result.items()):
            print(f"  {category}: {total}")
    except Exception as e:
        print(f"错误: 保存结果时发生异常: {e}")
        sys.exit(1)