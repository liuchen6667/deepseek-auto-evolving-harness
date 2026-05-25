def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """合并重叠的区间
    
    Args:
        intervals: 区间列表，每个区间是 [start, end]
    
    Returns:
        合并后的区间列表
    """
    if not intervals:
        return []
    
    # 按起始位置排序
    intervals.sort(key=lambda x: x[0])
    
    result = []
    for interval in intervals:
        # 如果结果为空，或者当前区间与最后一个区间不重叠
        if not result or interval[0] > result[-1][1]:
            result.append(interval)
        else:
            # 有重叠，合并区间
            result[-1][1] = max(result[-1][1], interval[1])
    
    return result