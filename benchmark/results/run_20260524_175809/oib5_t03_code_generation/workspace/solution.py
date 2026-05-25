def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """合并重叠的区间
    
    给定一个区间列表，合并所有重叠或相邻的区间。
    
    Args:
        intervals: 区间列表，每个区间是 [start, end]，其中 start <= end
    
    Returns:
        合并后的区间列表，按起点升序排列
    
    Examples:
        >>> merge_intervals([[1,3],[2,6],[8,10],[15,18]])
        [[1,6],[8,10],[15,18]]
        >>> merge_intervals([[1,2],[2,3]])
        [[1,3]]
        >>> merge_intervals([[1,4],[2,5],[3,6]])
        [[1,6]]
    """
    # 如果区间为空或只有一个区间，直接返回
    if len(intervals) <= 1:
        return intervals
    
    # 首先按区间起点排序
    intervals.sort(key=lambda x: x[0])
    
    # 初始化结果列表，放入第一个区间
    result = [intervals[0]]
    
    # 遍历剩余的区间
    for current in intervals[1:]:
        # 获取结果列表中最后一个区间
        last = result[-1]
        
        # 如果当前区间与最后一个区间重叠或相邻（current[0] <= last[1]）
        # 注意：相邻区间 [1,2] 和 [2,3] 应该合并，所以用 <= 而不是 <
        if current[0] <= last[1]:
            # 合并区间，取最大的结束点
            last[1] = max(last[1], current[1])
        else:
            # 不重叠，添加到结果中
            result.append(current)
    
    return result