#!/usr/bin/env python3

# Task information
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

# Resource constraints
MAX_CPU = 8
MAX_MEM = 16

def calculate_critical_path():
    """Calculate the critical path based on dependencies only"""
    # Forward pass to calculate earliest start times
    earliest_start = {task: 0 for task in tasks}
    changed = True
    while changed:
        changed = False
        for task, info in tasks.items():
            if info['deps']:
                new_start = max(earliest_start[dep] + tasks[dep]['duration'] for dep in info['deps'])
                if new_start > earliest_start[task]:
                    earliest_start[task] = new_start
                    changed = True
    
    # Backward pass to calculate latest start times
    # First find makespan without resources
    makespan_no_resources = max(earliest_start[task] + tasks[task]['duration'] for task in tasks)
    latest_start = {task: makespan_no_resources - tasks[task]['duration'] for task in tasks}
    
    changed = True
    while changed:
        changed = False
        for task, info in tasks.items():
            # Find tasks that depend on this task
            for dependent, dep_info in tasks.items():
                if task in dep_info['deps']:
                    new_latest = latest_start[dependent] - tasks[task]['duration']
                    if new_latest < latest_start[task]:
                        latest_start[task] = new_latest
                        changed = True
    
    # Critical tasks are those with zero slack
    critical_path = []
    for task in sorted(tasks.keys()):
        slack = latest_start[task] - earliest_start[task]
        if slack == 0:
            critical_path.append(task)
    
    # Order critical path by dependencies
    ordered_critical = []
    remaining = critical_path.copy()
    while remaining:
        for task in remaining:
            deps_in_critical = [dep for dep in tasks[task]['deps'] if dep in critical_path]
            if all(dep in ordered_critical for dep in deps_in_critical):
                ordered_critical.append(task)
                remaining.remove(task)
                break
    
    return ordered_critical, makespan_no_resources

critical_path, makespan_no_resources = calculate_critical_path()
print(f"Critical path (without resources): {critical_path}")
print(f"Makespan without resources: {makespan_no_resources}")

# Now let's try to schedule with resource constraints manually
print("\nLet's try manual scheduling with resource constraints:")
print("Time 0: A and B can start (CPU: 2+1=3, Mem: 4+2=6)")
print("  Resources used: CPU=3/8, Mem=6/16")
print("Time 2: A finishes, C and D become ready")
print("  B still running (ends at time 2)")
print("  At time 2, we could start C and/or D")
print("  Option 1: Start C (CPU=3, Mem=4) + B(CPU=1, Mem=2) = CPU=4, Mem=6")
print("  Option 2: Start D (CPU=2, Mem=3) + B(CPU=1, Mem=2) = CPU=3, Mem=5")
print("  Option 3: Start both C and D + B = CPU=6, Mem=9 - within limits")
print("  Best: Start both C and D at time 2 to minimize makespan")
print("\nLet's simulate step by step...")

# Let me create a simple simulation
def simulate_schedule():
    schedule = []
    current_time = 0
    completed = set()
    running = {}  # task -> end_time
    
    # Initial ready tasks: A and B
    ready = ['A', 'B']
    
    while len(completed) < len(tasks):
        # Check for tasks that finish at current_time
        finished = [task for task, end in running.items() if end <= current_time]
        for task in finished:
            del running[task]
            completed.add(task)
            
        # Update ready tasks
        for task, info in tasks.items():
            if task not in completed and task not in running and task not in ready:
                if all(dep in completed for dep in info['deps']):
                    ready.append(task)
        
        # Sort ready tasks alphabetically
        ready.sort()
        
        # Try to start as many ready tasks as possible
        started = []
        cpu_used = sum(tasks[task]['cpu'] for task in running)
        mem_used = sum(tasks[task]['mem'] for task in running)
        
        for task in ready[:]:  # Copy list
            cpu_needed = tasks[task]['cpu']
            mem_needed = tasks[task]['mem']
            
            if cpu_used + cpu_needed <= MAX_CPU and mem_used + mem_needed <= MAX_MEM:
                # Start this task
                start_time = current_time
                end_time = current_time + tasks[task]['duration']
                schedule.append({
                    'task': task,
                    'start': start_time,
                    'end': end_time
                })
                running[task] = end_time
                cpu_used += cpu_needed
                mem_used += mem_needed
                started.append(task)
                
        # Remove started tasks from ready
        for task in started:
            ready.remove(task)
        
        # If nothing started and no tasks running, advance time
        if not running and not started and ready:
            # Should not happen with our scheduling
            current_time += 1
        elif running:
            # Jump to next completion time
            next_completion = min(running.values())
            current_time = next_completion
        else:
            current_time += 1
            
    # Sort schedule by start time, then task
    schedule.sort(key=lambda x: (x['start'], x['task']))
    makespan = max(item['end'] for item in schedule)
    
    return schedule, makespan

schedule, makespan = simulate_schedule()
print("\nSchedule:")
for item in schedule:
    print(f"  {item['task']}: start={item['start']}, end={item['end']}")
print(f"Makespan: {makespan}")

# Calculate parallel groups
print("\nParallel groups (tasks with same start time):")
groups = {}
for item in schedule:
    groups.setdefault(item['start'], []).append(item['task'])

parallel_groups = []
for start_time in sorted(groups.keys()):
    parallel_groups.append(sorted(groups[start_time]))
    print(f"  Time {start_time}: {sorted(groups[start_time])}")

print(f"\nCritical path with resource constraints: {critical_path}")