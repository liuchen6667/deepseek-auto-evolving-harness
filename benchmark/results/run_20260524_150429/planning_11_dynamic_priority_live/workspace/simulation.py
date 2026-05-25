# 模拟动态优先级调度

# 初始状态
tasks = {
    'X': {'priority': 0, 'value': 8, 'deps': [], 'executed': False},
    'Z': {'priority': 0, 'value': 9, 'deps': [], 'executed': False},
    'M': {'priority': 1, 'value': 7, 'deps': [], 'executed': False},
    'Q': {'priority': 1, 'value': 5, 'deps': [], 'executed': False},
    'Y': {'priority': 1, 'value': 14, 'deps': ['Q'], 'executed': False},
    'N': {'priority': 2, 'value': 4, 'deps': [], 'executed': False}
}

# 记录执行顺序和值
execution_plan = []
total_value = 0

def get_available_tasks():
    """获取当前可执行的任务（依赖已满足且未执行）"""
    available = []
    for task_name, task_info in tasks.items():
        if not task_info['executed']:
            # 检查依赖
            deps_satisfied = True
            for dep in task_info['deps']:
                if not tasks[dep]['executed']:
                    deps_satisfied = False
                    break
            if deps_satisfied:
                available.append((task_name, task_info['priority'], task_info['value']))
    return available

def execute_task(task_name, slot_start):
    """执行任务并记录"""
    global total_value
    task_info = tasks[task_name]
    task_info['executed'] = True
    execution_plan.append({
        'slot_start': slot_start,
        'task': task_name,
        'value_at_execution': task_info['value']
    })
    total_value += task_info['value']
    print(f"Slot {slot_start}: 执行 {task_name} (P{task_info['priority']}, value={task_info['value']})")

# 时间槽0-5: [0,5)
print("=== 时间槽 [0,5) ===")
available = get_available_tasks()
print(f"可执行任务: {available}")

# 按优先级分组：P0最高，然后是P1，最后P2
p0_tasks = [(n, p, v) for n, p, v in available if p == 0]
p1_tasks = [(n, p, v) for n, p, v in available if p == 1]
p2_tasks = [(n, p, v) for n, p, v in available if p == 2]

# 优先执行最高优先级的任务
if p0_tasks:
    # 在同优先级内选择价值最高的
    selected = max(p0_tasks, key=lambda x: x[2])
    execute_task(selected[0], 0)
elif p1_tasks:
    selected = max(p1_tasks, key=lambda x: x[2])
    execute_task(selected[0], 0)
elif p2_tasks:
    selected = max(p2_tasks, key=lambda x: x[2])
    execute_task(selected[0], 0)

# 时间槽5-10: [5,10)
print("\n=== 时间槽 [5,10) ===")
print("应用T+5变化: 如果X还没执行，X的价值翻倍为16")
if not tasks['X']['executed']:
    tasks['X']['value'] = 16
    print(f"X的价值更新为16")

available = get_available_tasks()
print(f"可执行任务: {available}")

p0_tasks = [(n, p, v) for n, p, v in available if p == 0]
p1_tasks = [(n, p, v) for n, p, v in available if p == 1]
p2_tasks = [(n, p, v) for n, p, v in available if p == 2]

if p0_tasks:
    selected = max(p0_tasks, key=lambda x: x[2])
    execute_task(selected[0], 5)
elif p1_tasks:
    selected = max(p1_tasks, key=lambda x: x[2])
    execute_task(selected[0], 5)
elif p2_tasks:
    selected = max(p2_tasks, key=lambda x: x[2])
    execute_task(selected[0], 5)

# 时间槽10-15: [10,15)
print("\n=== 时间槽 [10,15) ===")
print("应用T+10变化: 新增A: P0, value=12；B: P0, value=11；C: P0, value=3")
tasks['A'] = {'priority': 0, 'value': 12, 'deps': [], 'executed': False}
tasks['B'] = {'priority': 0, 'value': 11, 'deps': [], 'executed': False}
tasks['C'] = {'priority': 0, 'value': 3, 'deps': [], 'executed': False}

available = get_available_tasks()
print(f"可执行任务: {available}")

p0_tasks = [(n, p, v) for n, p, v in available if p == 0]
p1_tasks = [(n, p, v) for n, p, v in available if p == 1]
p2_tasks = [(n, p, v) for n, p, v in available if p == 2]

if p0_tasks:
    selected = max(p0_tasks, key=lambda x: x[2])
    execute_task(selected[0], 10)
elif p1_tasks:
    selected = max(p1_tasks, key=lambda x: x[2])
    execute_task(selected[0], 10)
elif p2_tasks:
    selected = max(p2_tasks, key=lambda x: x[2])
    execute_task(selected[0], 10)

# 时间槽15-20: [15,20)
print("\n=== 时间槽 [15,20) ===")
print("应用T+15变化: Y的依赖被取消，变为可执行")
tasks['Y']['deps'] = []  # 取消依赖

available = get_available_tasks()
print(f"可执行任务: {available}")

p0_tasks = [(n, p, v) for n, p, v in available if p == 0]
p1_tasks = [(n, p, v) for n, p, v in available if p == 1]
p2_tasks = [(n, p, v) for n, p, v in available if p == 2]

if p0_tasks:
    selected = max(p0_tasks, key=lambda x: x[2])
    execute_task(selected[0], 15)
elif p1_tasks:
    selected = max(p1_tasks, key=lambda x: x[2])
    execute_task(selected[0], 15)
elif p2_tasks:
    selected = max(p2_tasks, key=lambda x: x[2])
    execute_task(selected[0], 15)

# 时间槽20-25: [20,25)
print("\n=== 时间槽 [20,25) ===")
print("应用T+20变化: 如果Z还没执行，Z降级为P2且价值变为1")
if not tasks['Z']['executed']:
    tasks['Z']['priority'] = 2
    tasks['Z']['value'] = 1
    print(f"Z降级为P2，价值变为1")

available = get_available_tasks()
print(f"可执行任务: {available}")

p0_tasks = [(n, p, v) for n, p, v in available if p == 0]
p1_tasks = [(n, p, v) for n, p, v in available if p == 1]
p2_tasks = [(n, p, v) for n, p, v in available if p == 2]

if p0_tasks:
    selected = max(p0_tasks, key=lambda x: x[2])
    execute_task(selected[0], 20)
elif p1_tasks:
    selected = max(p1_tasks, key=lambda x: x[2])
    execute_task(selected[0], 20)
elif p2_tasks:
    selected = max(p2_tasks, key=lambda x: x[2])
    execute_task(selected[0], 20)

print(f"\n=== 最终结果 ===")
print(f"执行计划: {execution_plan}")
print(f"总价值: {total_value}")