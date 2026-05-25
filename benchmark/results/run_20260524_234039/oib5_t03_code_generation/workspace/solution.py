def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """
    合并重叠的区间
    
    Args:
        intervals: 区间列表，每个区间是 [start, end] 的列表
        
    Returns:
        合并后的区间列表
    """
    if not intervals:
        return []
    
    # 先按区间起点排序
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    current_start, current_end = intervals[0]
    
    for start, end in intervals[1:]:
        # 如果当前区间与下一个区间重叠或相邻（start <= current_end）
        if start <= current_end:
            # 更新当前区间的结束时间为最大值
            current_end = max(current_end, end)
        else:
            # 没有重叠，将当前区间添加到结果中
            merged.append([current_start, current_end])
            # 开始新的区间
            current_start, current_end = start, end
    
    # 添加最后一个区间
    merged.append([current_start, current_end])
    
    return merged