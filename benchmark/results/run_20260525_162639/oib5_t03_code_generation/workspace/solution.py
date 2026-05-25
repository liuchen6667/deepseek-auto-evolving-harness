def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """合并所有重叠的区间
    
    Args:
        intervals: 区间列表，每个区间为 [start, end]
        
    Returns:
        合并后的区间列表
    """
    if not intervals:
        return []
    
    # 按区间起点排序
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    current = intervals[0]
    
    for interval in intervals[1:]:
        # 如果当前区间与下一个区间有重叠（包括相邻区间）
        if current[1] >= interval[0]:
            # 合并区间，取最大的结束点
            current[1] = max(current[1], interval[1])
        else:
            merged.append(current)
            current = interval
    
    merged.append(current)
    return merged