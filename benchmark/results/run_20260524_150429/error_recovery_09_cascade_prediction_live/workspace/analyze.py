import json

# 依赖关系
edges = [
    ('A', 'B'),  # A -> B
    ('A', 'C'),  # A -> C
    ('B', 'D'),  # B -> D
    ('C', 'E'),  # C -> E
    ('F', 'D'),  # F -> D
    ('G', 'E'),  # G -> E
    ('H', 'E'),  # H -> E
]

# 反向依赖映射（谁依赖我）
dependents = {}
for src, dst in edges:
    if dst not in dependents:
        dependents[dst] = []
    dependents[dst].append(src)

print('反向依赖关系:')
for service, deps in dependents.items():
    print(f'  {service}: {deps}')

# 维护计划
maintenance = {
    'D': 'down',      # 完全停机
    'E': 'degraded',  # 降级
}

# 所有服务
all_services = set()
for src, dst in edges:
    all_services.add(src)
    all_services.add(dst)

print(f'\n所有服务: {sorted(all_services)}')
print(f'\n维护计划: {maintenance}')

# 直接影响：直接依赖 D 或 E 的服务
direct_impacts = []
for service in all_services:
    # 检查服务是否直接依赖 D 或 E
    for src, dst in edges:
        if src == service and dst in ['D', 'E']:
            if service not in direct_impacts:
                direct_impacts.append(service)

print(f'\n直接影响: {sorted(direct_impacts)}')

# 间接影响：依赖已受影响服务的服务
affected = set(direct_impacts)
# 添加 D 和 E 本身，因为它们被维护
affected.add('D')
affected.add('E')

changed = True
while changed:
    changed = False
    for src, dst in edges:
        if dst in affected and src not in affected:
            affected.add(src)
            changed = True

indirect_impacts = []
for service in affected:
    if service not in direct_impacts and service not in ['D', 'E']:
        indirect_impacts.append(service)

print(f'\n所有受影响服务: {sorted(affected)}')
print(f'间接影响: {sorted(indirect_impacts)}')

# 风险等级
risk_levels = {}
for service in all_services:
    if service not in affected:
        continue
    
    # 收集服务的依赖
    deps = []
    for src, dst in edges:
        if src == service:
            deps.append(dst)
    
    # 检查是否依赖停机服务
    has_down_dependency = any(dep == 'D' for dep in deps)
    
    # 检查是否依赖两个已受影响上游
    affected_deps = [dep for dep in deps if dep in affected]
    has_two_affected = len(affected_deps) >= 2
    
    # 检查是否只依赖降级服务
    only_degraded = all(dep == 'E' for dep in deps) and len(deps) > 0
    
    if has_down_dependency or has_two_affected:
        risk = 'high'
    elif only_degraded:
        risk = 'medium'
    else:
        risk = 'low'
    
    risk_levels[service] = risk

print(f'\n风险等级: {risk_levels}')

# 恢复优先级
recovery_priority = []

# 1. 根因服务（D和E）
recovery_priority.append('D')  # 停机服务优先级更高
recovery_priority.append('E')

# 2. 直接受影响服务
for service in sorted(direct_impacts):
    if service not in recovery_priority:
        recovery_priority.append(service)

# 3. 间接受影响服务
for service in sorted(indirect_impacts):
    if service not in recovery_priority:
        recovery_priority.append(service)

print(f'\n恢复优先级: {recovery_priority}')

# 输出最终结果
result = {
    'direct_impacts': sorted(direct_impacts),
    'indirect_impacts': sorted(indirect_impacts),
    'risk_levels': risk_levels,
    'recovery_priority': recovery_priority,
    'notes': [
        '关键传播链路：D停机直接影响B和F，进而影响A；E降级直接影响C、G、H，进而影响A',
        '缓解思路：优先恢复D以解除对B和F的影响，然后恢复E以改善C、G、H的性能'
    ]
}

print('\n最终结果:')
print(json.dumps(result, indent=2))
