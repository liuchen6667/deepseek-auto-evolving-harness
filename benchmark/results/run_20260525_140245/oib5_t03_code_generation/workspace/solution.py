def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """合并重叠区间
    
    Args:
        intervals: 区间列表，每个区间是 [start, end]
    
    Returns:
        合并后的区间列表
    """
    if not intervals:
        return []
    
    # 按起始位置排序
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    current_start, current_end = intervals[0]
    
    for i in range(1, len(intervals)):
        next_start, next_end = intervals[i]
        
        # 如果当前区间与下一个区间重叠或相邻（当前结束 >= 下一个开始）
        if current_end >= next_start:
            # 合并：取最大的结束位置
            current_end = max(current_end, next_end)
        else:
            # 不重叠，保存当前区间，开始新的区间
            merged.append([current_start, current_end])
            current_start, current_end = next_start, next_end
    
    # 添加最后一个区间
    merged.append([current_start, current_end])
    
    return merged