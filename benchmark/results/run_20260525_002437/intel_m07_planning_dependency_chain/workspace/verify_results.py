import json

def verify_results():
    # 读取原始任务
    with open('tasks.json', 'r') as f:
        tasks_data = json.load(f)
    tasks = tasks_data['tasks']
    
    # 读取执行计划
    with open('execution_plan.json', 'r') as f:
        plan = json.load(f)
    
    print("=== 验证执行计划 ===")
    
    # 1. 验证拓扑排序
    print("\n1. 拓扑排序验证:")
    execution_order = plan['execution_order']
    print(f"执行顺序: {execution_order}")
    
    # 检查依赖关系是否满足
    task_dict = {task['id']: task for task in tasks}
    valid = True
    for i, task_id in enumerate(execution_order):
        task = task_dict[task_id]
        for dep in task['depends_on']:
            if dep not in execution_order[:i]:
                print(f"错误: 任务 {task_id} 依赖 {dep}，但 {dep} 不在其前面")
                valid = False
    
    if valid:
        print("✓ 拓扑排序有效: 所有依赖关系都满足")
    
    # 2. 验证关键路径
    print("\n2. 关键路径验证:")
    critical_path = plan['critical_path_task_ids']
    critical_duration = plan['critical_path_minutes']
    
    # 计算关键路径时长
    calculated_duration = sum(task_dict[task_id]['duration_minutes'] for task_id in critical_path)
    print(f"关键路径: {critical_path}")
    print(f"声明的时长: {critical_duration} 分钟")
    print(f"计算的时长: {calculated_duration} 分钟")
    
    if critical_duration == calculated_duration:
        print("✓ 关键路径时长正确")
    
    # 检查关键路径是否连续
    for i in range(1, len(critical_path)):
        current = critical_path[i]
        prev = critical_path[i-1]
        if prev not in task_dict[current]['depends_on']:
            # 检查是否有间接依赖
            # 简单检查：prev是否在current的任何依赖的依赖链中
            def is_in_dependency_chain(task_id, target, visited=None):
                if visited is None:
                    visited = set()
                if task_id in visited:
                    return False
                visited.add(task_id)
                
                if target in task_dict[task_id]['depends_on']:
                    return True
                
                for dep in task_dict[task_id]['depends_on']:
                    if is_in_dependency_chain(dep, target, visited):
                        return True
                return False
            
            if not is_in_dependency_chain(current, prev):
                print(f"警告: 关键路径中 {prev} 不是 {current} 的直接或间接依赖")
    
    # 3. 验证最早开始时间
    print("\n3. 最早开始时间验证:")
    earliest_start = plan['earliest_start_minutes']
    
    # 重新计算最早开始时间
    def calculate_earliest_start():
        est = {}
        for task_id in execution_order:
            task = task_dict[task_id]
            if not task['depends_on']:
                est[task_id] = 0
            else:
                max_finish = 0
                for dep in task['depends_on']:
                    dep_finish = est[dep] + task_dict[dep]['duration_minutes']
                    if dep_finish > max_finish:
                        max_finish = dep_finish
                est[task_id] = max_finish
        return est
    
    recalculated_est = calculate_earliest_start()
    
    all_correct = True
    for task_id in earliest_start:
        if earliest_start[task_id] != recalculated_est[task_id]:
            print(f"错误: 任务 {task_id} 的最早开始时间不正确")
            print(f"  声明的: {earliest_start[task_id]}, 计算的: {recalculated_est[task_id]}")
            all_correct = False
    
    if all_correct:
        print("✓ 所有最早开始时间正确")
    
    # 4. 验证并行分组
    print("\n4. 并行分组验证:")
    parallel_groups = plan['parallel_groups']
    
    # 检查同一组内的任务是否有相同的开始时间
    for i, group in enumerate(parallel_groups):
        if len(group) > 1:
            start_times = [earliest_start[task_id] for task_id in group]
            if len(set(start_times)) > 1:
                print(f"警告: 第 {i+1} 组中的任务开始时间不同: {list(zip(group, start_times))}")
            else:
                print(f"组 {i+1}: {group} 都在时间 {start_times[0]} 开始")
        else:
            print(f"组 {i+1}: {group} 在时间 {earliest_start[group[0]]} 开始")
    
    # 5. 验证循环依赖
    print("\n5. 循环依赖验证:")
    has_cycle = plan['has_cycle']
    
    # 简单检查：如果拓扑排序包含所有任务，则无环
    if set(execution_order) == set(task_dict.keys()):
        if not has_cycle:
            print("✓ 无循环依赖 (所有任务都在拓扑排序中)")
        else:
            print("错误: 检测到循环依赖，但所有任务都在拓扑排序中")
    else:
        if has_cycle:
            print("✓ 检测到循环依赖")
        else:
            print("错误: 未检测到循环依赖，但拓扑排序不包含所有任务")
    
    print("\n=== 验证完成 ===")

if __name__ == "__main__":
    verify_results()