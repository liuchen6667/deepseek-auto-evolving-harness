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
    current_start, current_end = intervals[0]
    
    for start, end in intervals[1:]:
        # 如果当前区间与下一个区间重叠或相邻（start <= current_end）
        if start <= current_end:
            # 合并区间，取最大的结束值
            current_end = max(current_end, end)
        else:
            # 保存当前合并的区间，开始处理下一个区间
            merged.append([current_start, current_end])
            current_start, current_end = start, end
    
    # 添加最后一个区间
    merged.append([current_start, current_end])
    
    return merged