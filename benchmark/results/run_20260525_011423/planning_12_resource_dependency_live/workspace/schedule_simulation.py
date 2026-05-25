#!/usr/bin/env python3
"""
验证调度方案
"""

tasks = {
    'A': {'duration': 2, 'cpu': 2, 'mem': 4, 'deps': []},
    'B': {'duration': 2, 'cpu': 1, 'mem': 2, 'deps': []},
    'C': {'duration': 3, 'cpu': 3, 'mem': 4, 'deps': ['A']},
    'D': {'duration': 2, 'cpu': 2, 'mem': 3, 'deps': ['A']},
    'E': {'duration': 4, 'cpu': 4, 'mem': 6, 'deps': ['B', 'C']},
    'F': {'duration': 3, 'cpu': 3, 'mem': 4, 'deps': ['D']},
    'G': {'duration': 5, 'cpu': 5, 'mem': 8, 'deps': ['E', 'F']},
    'H': {'duration': 1, 'cpu': 1, 'mem': 2, 'deps': ['E']},
    'I': {'duration': 2, 'cpu': 2, 'mem': 2, 'deps': ['G', 'H']}
}

# 基于最早开始时间的调度
schedule = {
    'A': {'start': 0, 'end': 2},
    'B': {'start': 0, 'end': 2},
    'C': {'start': 2, 'end': 5},
    'D': {'start': 2, 'end': 4},
    'E': {'start': 5, 'end': 9},
    'F': {'start': 4, 'end': 7},
    'G': {'start': 9, 'end': 14},
    'H': {'start': 9, 'end': 10},
    'I': {'start': 14, 'end': 16}
}

# 验证依赖关系
def validate_dependencies():
    print("=== 依赖关系验证 ===")
    all_valid = True
    for task, times in schedule.items():
        start = times['start']
        deps = tasks[task]['deps']
        
        for dep in deps:
            dep_end = schedule[dep]['end']
            if start < dep_end:
                print(f"错误: 任务 {task} 在时间 {start} 开始，但其依赖 {dep} 在时间 {dep_end} 才结束")
                all_valid = False
    
    if all_valid:
        print("所有依赖关系满足！")
    return all_valid

# 验证资源约束
def validate_resources():
    print("\n=== 资源约束验证 ===")
    
    # 收集所有时间点
    time_points = set()
    for task, times in schedule.items():
        time_points.add(times['start'])
        time_points.add(times['end'])
    
    time_points = sorted(time_points)
    
    resource_limits = {'cpu': 8, 'mem': 16}
    all_valid = True
    
    for t in time_points:
        cpu_usage = 0
        mem_usage = 0
        active_tasks = []
        
        for task, times in schedule.items():
            start = times['start']
            end = times['end']
            if start <= t < end:
                cpu_usage += tasks[task]['cpu']
                mem_usage += tasks[task]['mem']
                active_tasks.append(task)
        
        cpu_ok = cpu_usage <= resource_limits['cpu']
        mem_ok = mem_usage <= resource_limits['mem']
        
        status = "✓" if cpu_ok and mem_ok else "✗"
        print(f"时间 {t}: CPU={cpu_usage}/{resource_limits['cpu']} {status if cpu_ok else '超限!'}, "
              f"Memory={mem_usage}/{resource_limits['mem']} {status if mem_ok else '超限!'}, "
              f"活动任务: {active_tasks}")
        
        if not cpu_ok or not mem_ok:
            all_valid = False
    
    if all_valid:
        print("所有资源约束满足！")
    else:
        print("资源约束不满足！")
    
    return all_valid

# 验证调度顺序
def validate_schedule_order():
    print("\n=== 调度顺序验证 ===")
    
    # 检查是否有任务可以更早开始
    for task, times in schedule.items():
        start = times['start']
        deps = tasks[task]['deps']
        
        # 计算最早可能开始时间（基于依赖完成）
        earliest_possible = 0
        for dep in deps:
            dep_end = schedule[dep]['end']
            if dep_end > earliest_possible:
                earliest_possible = dep_end
        
        if start > earliest_possible:
            print(f"任务 {task} 可以在时间 {earliest_possible} 开始，但实际在 {start} 开始")
        elif start < earliest_possible:
            print(f"警告: 任务 {task} 在时间 {start} 开始，但其依赖在 {earliest_possible} 才完成！")
    
    print("调度顺序验证完成")

if __name__ == "__main__":
    deps_ok = validate_dependencies()
    resources_ok = validate_resources()
    validate_schedule_order()
    
    if deps_ok and resources_ok:
        print("\n✓ 调度方案有效！")
        print(f"总工期: {max(t['end'] for t in schedule.values())}")
    else:
        print("\n✗ 调度方案无效！")