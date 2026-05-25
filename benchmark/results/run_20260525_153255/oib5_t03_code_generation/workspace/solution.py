def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """
    合并所有重叠的区间。
    
    参数:
        intervals: 区间列表，每个区间为 [start, end]
        
    返回:
        合并后的区间列表
    """
    if not intervals:
        return []
    
    # 按区间起始位置排序
    intervals.sort(key=lambda x: x[0])
    
    merged = []
    current_start, current_end = intervals[0]
    
    for start, end in intervals[1:]:
        # 如果当前区间与下一个区间重叠或相邻（start <= current_end）
        if start <= current_end:
            # 更新当前区间的结束位置为两者中较大的
            current_end = max(current_end, end)
        else:
            # 不重叠，保存当前区间，开始新的区间
            merged.append([current_start, current_end])
            current_start, current_end = start, end
    
    # 添加最后一个区间
    merged.append([current_start, current_end])
    
    return merged