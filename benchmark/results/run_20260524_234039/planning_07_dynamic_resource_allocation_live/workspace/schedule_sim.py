import json

# 读取数据
with open('resource_windows.json') as f:
    windows = json.load(f)['windows']

with open('task_catalog.json') as f:
    tasks = json.load(f)['tasks']

with open('baseline_service.json') as f:
    baseline_res = json.load(f)['resource_reservation']

# 窗口资源映射
window_resources = {w['window_id']: {'cpu': w['cpu'], 'ram': w['ram_gb']} for w in windows}
window_minutes = {w['window_id']: w['minutes'] for w in windows}

# 任务映射
task_info = {t['task_id']: t for t in tasks}

# 优先级排序：p0 > p1 > p2 > p3
priority_order = {'p0': 0, 'p1': 1, 'p2': 2, 'p3': 3}

# 模拟调度
def simulate_schedule():
    scheduled = {}
    available_windows = ['window_1', 'window_2', 'window_3', 'window_4']
    
    # 首先，stream_restore必须在window_1
    scheduled['stream_restore'] = {'start': 'window_1', 'windows': 1}
    
    # 计算每个窗口已用资源
    window_usage = {w: {'cpu': baseline_res['cpu'], 'ram': baseline_res['ram_gb']} for w in available_windows}
    window_usage['window_1']['cpu'] += task_info['stream_restore']['cpu']
    window_usage['window_1']['ram'] += task_info['stream_restore']['ram_gb']
    
    # 检查window_1剩余容量
    avail_cpu_1 = window_resources['window_1']['cpu'] - window_usage['window_1']['cpu']
    avail_ram_1 = window_resources['window_1']['ram'] - window_usage['window_1']['ram']
    
    print(f"Window_1: 已用 {window_usage['window_1']['cpu']} cpu, {window_usage['window_1']['ram']} ram_gb")
    print(f"Window_1: 剩余 {avail_cpu_1} cpu, {avail_ram_1} ram_gb")
    
    # 尝试在window_1调度ingestion_repair（为analytics_rollup做准备）
    if (avail_cpu_1 >= task_info['ingestion_repair']['cpu'] and 
        avail_ram_1 >= task_info['ingestion_repair']['ram_gb']):
        scheduled['ingestion_repair'] = {'start': 'window_1', 'windows': 1}
        window_usage['window_1']['cpu'] += task_info['ingestion_repair']['cpu']
        window_usage['window_1']['ram'] += task_info['ingestion_repair']['ram_gb']
        print(f"Window_1: 添加 ingestion_repair")
    
    # 检查window_2-3是否可以运行analytics_rollup（需要2个连续窗口）
    if 'ingestion_repair' in scheduled:
        # analytics_rollup需要5 cpu, 10 ram每个窗口
        can_fit_window2 = (window_resources['window_2']['cpu'] - window_usage['window_2']['cpu'] >= task_info['analytics_rollup']['cpu'] and
                          window_resources['window_2']['ram'] - window_usage['window_2']['ram'] >= task_info['analytics_rollup']['ram_gb'])
        can_fit_window3 = (window_resources['window_3']['cpu'] - window_usage['window_3']['cpu'] >= task_info['analytics_rollup']['cpu'] and
                          window_resources['window_3']['ram'] - window_usage['window_3']['ram'] >= task_info['analytics_rollup']['ram_gb'])
        
        if can_fit_window2 and can_fit_window3:
            scheduled['analytics_rollup'] = {'start': 'window_2', 'windows': 2}
            window_usage['window_2']['cpu'] += task_info['analytics_rollup']['cpu']
            window_usage['window_2']['ram'] += task_info['analytics_rollup']['ram_gb']
            window_usage['window_3']['cpu'] += task_info['analytics_rollup']['cpu']
            window_usage['window_3']['ram'] += task_info['analytics_rollup']['ram_gb']
            print(f"Window_2-3: 添加 analytics_rollup")
            
            # 然后可以在window_4添加cache_rebuild
            if (window_resources['window_4']['cpu'] - window_usage['window_4']['cpu'] >= task_info['cache_rebuild']['cpu'] and
                window_resources['window_4']['ram'] - window_usage['window_4']['ram'] >= task_info['cache_rebuild']['ram_gb']):
                scheduled['cache_rebuild'] = {'start': 'window_4', 'windows': 1}
                window_usage['window_4']['cpu'] += task_info['cache_rebuild']['cpu']
                window_usage['window_4']['ram'] += task_info['cache_rebuild']['ram_gb']
                print(f"Window_4: 添加 cache_rebuild")
    
    # 检查是否可以调度model_refresh（需要3个连续窗口）
    # 尝试window_1-3或window_2-4
    model_fits = False
    
    # 尝试window_1-3
    fits_1 = (window_resources['window_1']['cpu'] - window_usage['window_1']['cpu'] >= task_info['model_refresh']['cpu'] and
              window_resources['window_1']['ram'] - window_usage['window_1']['ram'] >= task_info['model_refresh']['ram_gb'])
    fits_2 = (window_resources['window_2']['cpu'] - window_usage['window_2']['cpu'] >= task_info['model_refresh']['cpu'] and
              window_resources['window_2']['ram'] - window_usage['window_2']['ram'] >= task_info['model_refresh']['ram_gb'])
    fits_3 = (window_resources['window_3']['cpu'] - window_usage['window_3']['cpu'] >= task_info['model_refresh']['cpu'] and
              window_resources['window_3']['ram'] - window_usage['window_3']['ram'] >= task_info['model_refresh']['ram_gb'])
    
    if fits_1 and fits_2 and fits_3:
        scheduled['model_refresh'] = {'start': 'window_1', 'windows': 3}
        print(f"Window_1-3: 可以添加 model_refresh")
        model_fits = True
    
    # 尝试window_2-4
    if not model_fits:
        fits_2 = (window_resources['window_2']['cpu'] - window_usage['window_2']['cpu'] >= task_info['model_refresh']['cpu'] and
                  window_resources['window_2']['ram'] - window_usage['window_2']['ram'] >= task_info['model_refresh']['ram_gb'])
        fits_3 = (window_resources['window_3']['cpu'] - window_usage['window_3']['cpu'] >= task_info['model_refresh']['cpu'] and
                  window_resources['window_3']['ram'] - window_usage['window_3']['ram'] >= task_info['model_refresh']['ram_gb'])
        fits_4 = (window_resources['window_4']['cpu'] - window_usage['window_4']['cpu'] >= task_info['model_refresh']['cpu'] and
                  window_resources['window_4']['ram'] - window_usage['window_4']['ram'] >= task_info['model_refresh']['ram_gb'])
        
        if fits_2 and fits_3 and fits_4:
            scheduled['model_refresh'] = {'start': 'window_2', 'windows': 3}
            print(f"Window_2-4: 可以添加 model_refresh")
            model_fits = True
    
    # 检查feature_backfill任务
    remaining_tasks = ['feature_backfill_a', 'feature_backfill_b']
    for task_id in remaining_tasks:
        task = task_info[task_id]
        # 尝试找到可以容纳的窗口
        for w in available_windows:
            if (window_resources[w]['cpu'] - window_usage[w]['cpu'] >= task['cpu'] and
                window_resources[w]['ram'] - window_usage[w]['ram'] >= task['ram_gb']):
                scheduled[task_id] = {'start': w, 'windows': 1}
                window_usage[w]['cpu'] += task['cpu']
                window_usage[w]['ram'] += task['ram_gb']
                print(f"{w}: 添加 {task_id}")
                break
    
    return scheduled, window_usage

scheduled, window_usage = simulate_schedule()
print("\n调度结果:")
for task, info in scheduled.items():
    print(f"{task}: 从 {info['start']} 开始，持续 {info['windows']} 窗口")

print("\n窗口使用情况:")
for w in ['window_1', 'window_2', 'window_3', 'window_4']:
    avail_cpu = window_resources[w]['cpu'] - window_usage[w]['cpu']
    avail_ram = window_resources[w]['ram'] - window_usage[w]['ram']
    print(f"{w}: 已用 {window_usage[w]['cpu']} cpu, {window_usage[w]['ram']} ram_gb, 剩余 {avail_cpu} cpu, {avail_ram} ram_gb")
