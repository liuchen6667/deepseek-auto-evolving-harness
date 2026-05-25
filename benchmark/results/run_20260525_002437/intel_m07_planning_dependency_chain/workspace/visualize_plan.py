import json

def visualize_plan():
    # 读取执行计划
    with open('execution_plan.json', 'r') as f:
        plan = json.load(f)
    
    # 读取原始任务
    with open('tasks.json', 'r') as f:
        tasks_data = json.load(f)
    tasks = tasks_data['tasks']
    
    task_dict = {task['id']: task for task in tasks}
    earliest_start = plan['earliest_start_minutes']
    critical_path = set(plan['critical_path_task_ids'])
    
    print("=== 项目执行计划甘特图 ===")
    print("\n任务ID | 任务名称           | 时长(分) | 开始时间 | 结束时间 | 关键路径")
    print("-" * 70)
    
    for task_id in plan['execution_order']:
        task = task_dict[task_id]
        start = earliest_start[task_id]
        duration = task['duration_minutes']
        end = start + duration
        is_critical = "✓" if task_id in critical_path else ""
        
        print(f"{task_id:6} | {task['name']:18} | {duration:8} | {start:8} | {end:8} | {is_critical}")
    
    print("\n=== 并行执行组 ===")
    for i, group in enumerate(plan['parallel_groups'], 1):
        if len(group) == 1:
            task_id = group[0]
            task = task_dict[task_id]
            print(f"组 {i}: {task_id} ({task['name']}) - 开始时间: {earliest_start[task_id]}分钟")
        else:
            print(f"组 {i}: {', '.join(group)} - 开始时间: {earliest_start[group[0]]}分钟")
            for task_id in group:
                task = task_dict[task_id]
                print(f"     {task_id}: {task['name']} ({task['duration_minutes']}分钟)")
    
    print("\n=== 关键路径分析 ===")
    print(f"关键路径: {' → '.join(plan['critical_path_task_ids'])}")
    print(f"总时长: {plan['critical_path_minutes']}分钟")
    
    # 显示关键路径上的任务详情
    total = 0
    for task_id in plan['critical_path_task_ids']:
        task = task_dict[task_id]
        duration = task['duration_minutes']
        total += duration
        print(f"  {task_id}: {task['name']} ({duration}分钟) [累计: {total}分钟]")
    
    print("\n=== 项目总时长 ===")
    finish_times = [earliest_start[task_id] + task_dict[task_id]['duration_minutes'] 
                   for task_id in task_dict]
    project_duration = max(finish_times)
    print(f"项目总时长: {project_duration}分钟")
    
    # 显示时间线
    print("\n=== 时间线 ===")
    max_time = project_duration
    scale = 5  # 每个字符代表5分钟
    
    for task_id in plan['execution_order']:
        task = task_dict[task_id]
        start = earliest_start[task_id]
        duration = task['duration_minutes']
        end = start + duration
        
        # 创建时间线表示
        timeline = [' '] * (max_time // scale + 1)
        
        # 标记任务时间段
        for t in range(start, end):
            if t // scale < len(timeline):
                timeline[t // scale] = '█' if task_id in critical_path else '░'
        
        # 显示时间线
        time_labels = ''.join([f"{i*scale:3}" for i in range(len(timeline))])
        timeline_str = ''.join(timeline)
        
        print(f"{task_id} ({task['name'][:15]}):")
        print(f"  时间: {time_labels}")
        print(f"  任务: {timeline_str}")
        print()

if __name__ == "__main__":
    visualize_plan()