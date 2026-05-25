#!/usr/bin/env python3

# 初始任务
initial_tasks = {
    'X': {'priority': 0, 'value': 8, 'dependencies': [], 'executed': False},
    'Z': {'priority': 0, 'value': 9, 'dependencies': [], 'executed': False},
    'M': {'priority': 1, 'value': 7, 'dependencies': [], 'executed': False},
    'Q': {'priority': 1, 'value': 5, 'dependencies': [], 'executed': False},
    'Y': {'priority': 1, 'value': 14, 'dependencies': ['Q'], 'executed': False},
    'N': {'priority': 2, 'value': 4, 'dependencies': [], 'executed': False}
}

# 时间槽
time_slots = [0, 5, 10, 15, 20]

def get_available_tasks(tasks):
    """获取当前可执行的任务（无依赖或依赖已执行）"""
    available = []
    for task_name, task_info in tasks.items():
        if task_info['executed']:
            continue
        # 检查依赖
        dependencies_met = True
        for dep in task_info['dependencies']:
            if dep in tasks and not tasks[dep]['executed']:
                dependencies_met = False
                break
        if dependencies_met:
            available.append((task_name, task_info))
    return available

def simulate_schedule():
    tasks = {name: info.copy() for name, info in initial_tasks.items()}
    schedule = []
    total_value = 0
    
    for slot_start in time_slots:
        # 应用该时间点的动态变化
        if slot_start == 5:
            # T+5: 如果 X 还没执行，X 的价值翻倍为 16
            if not tasks['X']['executed']:
                tasks['X']['value'] = 16
                print(f"T+5: X value doubled to 16")
        
        elif slot_start == 10:
            # T+10: 新增 A: P0, value=12；B: P0, value=11；C: P0, value=3
            tasks['A'] = {'priority': 0, 'value': 12, 'dependencies': [], 'executed': False}
            tasks['B'] = {'priority': 0, 'value': 11, 'dependencies': [], 'executed': False}
            tasks['C'] = {'priority': 0, 'value': 3, 'dependencies': [], 'executed': False}
            print(f"T+10: Added tasks A(P0,12), B(P0,11), C(P0,3)")
        
        elif slot_start == 15:
            # T+15: Y 的依赖被取消，变为可执行
            tasks['Y']['dependencies'] = []
            print(f"T+15: Y dependencies removed, now executable")
        
        elif slot_start == 20:
            # T+20: 如果 Z 还没执行，Z 降级为 P2 且价值变为 1
            if not tasks['Z']['executed']:
                tasks['Z']['priority'] = 2
                tasks['Z']['value'] = 1
                print(f"T+20: Z downgraded to P2 with value 1")
        
        # 获取当前可执行任务
        available_tasks = get_available_tasks(tasks)
        
        if not available_tasks:
            print(f"No available tasks at slot {slot_start}")
            schedule.append((slot_start, None, 0))
            continue
        
        # 按优先级分组
        priority_groups = {}
        for task_name, task_info in available_tasks:
            prio = task_info['priority']
            if prio not in priority_groups:
                priority_groups[prio] = []
            priority_groups[prio].append((task_name, task_info))
        
        # 找到最高优先级（数字最小）
        highest_prio = min(priority_groups.keys())
        
        # 在同优先级内，选择价值最高的任务
        candidates = priority_groups[highest_prio]
        # 按价值降序排序
        candidates.sort(key=lambda x: x[1]['value'], reverse=True)
        
        chosen_task_name, chosen_task_info = candidates[0]
        
        # 执行任务
        tasks[chosen_task_name]['executed'] = True
        value_at_execution = chosen_task_info['value']
        total_value += value_at_execution
        
        schedule.append((slot_start, chosen_task_name, value_at_execution))
        
        print(f"Slot {slot_start}: Executed {chosen_task_name} (P{chosen_task_info['priority']}, value={value_at_execution})")
    
    return schedule, total_value, tasks

if __name__ == "__main__":
    schedule, total_value, final_tasks = simulate_schedule()
    
    print("\nFinal Schedule:")
    for slot_start, task, value in schedule:
        print(f"  Slot {slot_start}: {task if task else 'None'} (value={value})")
    
    print(f"\nTotal Value: {total_value}")
    
    print("\nRemaining tasks (not executed):")
    for task_name, task_info in final_tasks.items():
        if not task_info['executed']:
            print(f"  {task_name}: P{task_info['priority']}, value={task_info['value']}")