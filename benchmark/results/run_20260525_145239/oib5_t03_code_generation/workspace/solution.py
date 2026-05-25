from typing import List

def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []
    
    # 按区间起始排序
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    current_start, current_end = intervals[0]
    
    for start, end in intervals[1:]:
        if start <= current_end:  # 重叠或相邻
            current_end = max(current_end, end)
        else:
            merged.append([current_start, current_end])
            current_start, current_end = start, end
    
    merged.append([current_start, current_end])
    return merged
