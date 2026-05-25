def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """合并所有重叠的区间"""
    if not intervals:
        return []
    
    # 首先按照区间起始位置排序（创建副本以避免修改原始输入）
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = []
    current_start, current_end = sorted_intervals[0]
    
    for start, end in sorted_intervals[1:]:
        # 如果当前区间与下一个区间重叠或相邻（当前区间的结束 >= 下一个区间的开始）
        if current_end >= start:
            # 合并区间，取最大的结束位置
            current_end = max(current_end, end)
        else:
            # 不重叠，将当前区间加入结果，更新当前区间
            merged.append([current_start, current_end])
            current_start, current_end = start, end
    
    # 添加最后一个区间
    merged.append([current_start, current_end])
    
    return merged
