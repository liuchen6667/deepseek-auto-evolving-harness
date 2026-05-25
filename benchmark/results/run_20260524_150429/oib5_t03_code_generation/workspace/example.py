#!/usr/bin/env python3
"""示例演示"""
from solution import merge_intervals

# 示例 1
intervals1 = [[1, 3], [2, 6], [8, 10], [15, 18]]
result1 = merge_intervals(intervals1)
print(f"示例1: {intervals1} => {result1}")
print(f"预期: [[1, 6], [8, 10], [15, 18]]")
print()

# 示例 2: 相邻区间
intervals2 = [[1, 2], [2, 3]]
result2 = merge_intervals(intervals2)
print(f"示例2 (相邻区间): {intervals2} => {result2}")
print(f"预期: [[1, 3]]")
print()

# 示例 3: 未排序输入
intervals3 = [[3, 5], [1, 4]]
result3 = merge_intervals(intervals3)
print(f"示例3 (未排序): {intervals3} => {result3}")
print(f"预期: [[1, 5]]")
print()

# 示例 4: 空输入
intervals4 = []
result4 = merge_intervals(intervals4)
print(f"示例4 (空输入): {intervals4} => {result4}")
print(f"预期: []")
