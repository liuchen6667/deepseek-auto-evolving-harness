import json

# 初始任务状态
tasks = {
    'X': {'priority': 0, 'value': 8, 'deps': [], 'executed': False},
    'Z': {'priority': 0, 'value': 9, 'deps': [], 'executed': False},
    'M': {'priority': 1, 'value': 7, 'deps': [], 'executed': False},
    'Q': {'priority': 1, 'value': 5, 'deps': [], 'executed': False},
    'Y': {'priority': 1, 'value': 14, 'deps': ['Q'], 'executed': False},
    'N': {'priority': 2, 'value': 4, 'deps': [], 'executed': False}
}

# 动态变化
events = {
    5: "如果 X 还没执行，X 的价值翻倍为 16",
    10: "新增 A: P0, value=12；B: P0, value=11；C: P0, value=3",
    15: "Y 的依赖被取消，变为可执行",
    20: "如果 Z 还没执行，Z 降级为 P2 且价值变为 1"
}

# 时间槽
slots = [0, 5, 10, 15, 20]

# 模拟调度过程
def simulate():
    schedule = []
    total_value = 0
    
    for slot_start in slots:
        print(f"\n=== 时间槽 [{slot_start},{slot_start+5}) ===")
        
        # 应用该时间点的动态变化
        if slot_start in events:
            event = events[slot_start]
            print(f"应用事件: {event}")
            
            if slot_start == 5:
                if not tasks['X']['executed']:
                    tasks['X']['value'] = 16
                    print(f"  X 价值翻倍为 16")
            
            elif slot_start == 10:
                tasks['A'] = {'priority': 0, 'value': 12, 'deps': [], 'executed': False}
                tasks['B'] = {'priority': 0, 'value': 11, 'deps': [], 'executed': False}
                tasks['C'] = {'priority': 0, 'value': 3, 'deps': [], 'executed': False}
                print(f"  新增任务 A(P0,12), B(P0,11), C(P0,3)")
            
            elif slot_start == 15:
                tasks['Y']['deps'] = []
                print(f"  Y 依赖取消，变为可执行")
            
            elif slot_start == 20:
                if not tasks['Z']['executed']:
                    tasks['Z']['priority'] = 2
                    tasks['Z']['value'] = 1
                    print(f"  Z 降级为 P2，价值变为 1")
        
        # 找出当前可执行的任务（依赖已满足且未执行）
        available_tasks = []
        for task_id, task_info in tasks.items():
            if not task_info['executed']:
                # 检查依赖是否满足
                deps_satisfied = True
                for dep in task_info['deps']:
                    if not tasks.get(dep, {}).get('executed', False):
                        deps_satisfied = False
                        break
                
                if deps_satisfied:
                    available_tasks.append((task_id, task_info['priority'], task_info['value']))
        
        print(f"当前可执行任务: {available_tasks}")
        
        if not available_tasks:
            print("警告: 没有可执行的任务！")
            schedule.append({'slot_start': slot_start, 'task': 'None', 'value_at_execution': 0})
            continue
        
        # 找出最高优先级
        min_priority = min(p for _, p, _ in available_tasks)
        highest_prio_tasks = [(t, p, v) for t, p, v in available_tasks if p == min_priority]
        
        print(f"最高优先级(P{min_priority})的任务: {highest_prio_tasks}")
        
        # 在同优先级内，选择价值最高的任务
        selected_task = max(highest_prio_tasks, key=lambda x: x[2])
        task_id, priority, value = selected_task
        
        print(f"选择任务: {task_id} (价值={value})")
        
        # 执行任务
        tasks[task_id]['executed'] = True
        total_value += value
        
        schedule.append({
            'slot_start': slot_start,
            'task': task_id,
            'value_at_execution': value
        })
    
    return schedule, total_value

# 运行模拟
schedule, total_value = simulate()

print(f"\n=== 最终调度结果 ===")
print(f"总价值: {total_value}")
print("调度计划:")
for item in schedule:
    print(f"  [{item['slot_start']},{item['slot_start']+5}): {item['task']} (价值={item['value_at_execution']})")

# 生成输出文件
output = {
    "slot_plan": schedule,
    "total_value": total_value,
    "events_considered": [
        "T+5: X 价值翻倍（如果未执行）影响早期决策",
        "T+10: 新增三个 P0 任务，增加了高优先级选项",
        "T+15: Y 依赖取消，使其在后期可执行",
        "T+20: Z 降级为 P2 价值降低，影响后期调度"
    ],
    "notes": [
        "优先执行最高优先级任务，同优先级内选择价值最高的",
        "考虑动态变化的时间点，在变化前执行可能价值更高的任务"
    ]
}

with open('priority_plan.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n结果已保存到 priority_plan.json")
