#!/usr/bin/env python3
# 分析级联故障预测

# 依赖关系
# X -> Y 表示 X 依赖 Y
# 如果 Y 不可用或降级，X 会受影响
dependencies = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['E'],
    'F': ['D'],
    'G': ['E'],
    'H': ['E']
}

# 维护计划
maintenance = {
    'D': '停机',  # 完全停机 2 小时
    'E': '降级'   # 降级到 50% 性能
}

# 构建反向依赖图（谁依赖我）
reverse_deps = {}
for service, deps in dependencies.items():
    for dep in deps:
        if dep not in reverse_deps:
            reverse_deps[dep] = []
        reverse_deps[dep].append(service)

print("反向依赖图:")
for dep, services in sorted(reverse_deps.items()):
    print(f"  {dep}: {services}")

# 直接影响：直接依赖 D 或 E 的服务
direct_impacts = []
for dep in ['D', 'E']:
    if dep in reverse_deps:
        direct_impacts.extend(reverse_deps[dep])

direct_impacts = sorted(list(set(direct_impacts)))
print(f"\n直接影响的服务: {direct_impacts}")

# 间接影响：依赖"已受影响服务"的服务
# 使用广度优先搜索
indirect_impacts = []
queue = direct_impacts.copy()
visited = set(direct_impacts)

while queue:
    service = queue.pop(0)
    # 如果这个服务有依赖它的其他服务
    if service in reverse_deps:
        for dependent in reverse_deps[service]:
            if dependent not in visited:
                indirect_impacts.append(dependent)
                visited.add(dependent)
                queue.append(dependent)

indirect_impacts = sorted(list(set(indirect_impacts)))
print(f"间接影响的服务: {indirect_impacts}")

# 风险等级计算
risk_levels = {}
all_affected = direct_impacts + indirect_impacts

for service in all_affected:
    # 获取这个服务的所有依赖
    deps = dependencies.get(service, [])
    
    # 检查是否有依赖停机服务
    has_stopped_dep = any(dep == 'D' for dep in deps)
    
    # 计算有多少个已受影响的上游
    affected_upstream_count = 0
    for dep in deps:
        if dep in ['D', 'E'] or dep in all_affected:
            affected_upstream_count += 1
    
    # 应用风险等级规则
    if has_stopped_dep or affected_upstream_count >= 2:
        risk_levels[service] = 'high'
    elif 'E' in deps and not has_stopped_dep:
        # 只依赖降级服务
        risk_levels[service] = 'medium'
    else:
        # 只通过单条间接链路受到影响
        risk_levels[service] = 'low'

print(f"\n风险等级: {risk_levels}")

# 恢复优先级
# 规则：先恢复造成影响范围更大的根因服务
# 再恢复直接受影响服务
# 最后恢复间接受影响服务
recovery_priority = []

# 1. 根因服务（D 和 E）
# D 的影响范围：B, F, A (通过B)
# E 的影响范围：C, G, H, A (通过C)
# 计算影响范围大小
d_impact_scope = set(['B', 'F'])
e_impact_scope = set(['C', 'G', 'H'])

# 通过B影响A
if 'B' in d_impact_scope:
    d_impact_scope.add('A')
# 通过C影响A    
if 'C' in e_impact_scope:
    e_impact_scope.add('A')

print(f"D的影响范围: {sorted(d_impact_scope)}")
print(f"E的影响范围: {sorted(e_impact_scope)}")

# D 影响 3 个服务（B, F, A）
# E 影响 4 个服务（C, G, H, A）
# 所以先恢复 E（影响范围更大），然后恢复 D
recovery_priority.extend(['E', 'D'])

# 2. 直接受影响服务
# 直接依赖 D 或 E 的服务
direct_deps_d = [s for s in direct_impacts if 'D' in dependencies.get(s, [])]
direct_deps_e = [s for s in direct_impacts if 'E' in dependencies.get(s, [])]

# 按字母排序并添加到优先级列表
direct_services = sorted(direct_impacts)
for service in direct_services:
    if service not in recovery_priority:
        recovery_priority.append(service)

# 3. 间接受影响服务
for service in indirect_impacts:
    if service not in recovery_priority:
        recovery_priority.append(service)

print(f"\n恢复优先级: {recovery_priority}")

# 生成最终结果
result = {
    "direct_impacts": direct_impacts,
    "indirect_impacts": indirect_impacts,
    "risk_levels": risk_levels,
    "recovery_priority": recovery_priority,
    "notes": [
        "关键传播链路：D 停机影响 B 和 F，进而影响 A；E 降级影响 C、G 和 H，进而影响 A",
        "缓解思路：优先恢复 E（影响 4 个服务），然后恢复 D（影响 3 个服务）；A 同时依赖 B 和 C，风险等级为 high"
    ]
}

print("\n最终结果:")
import json
print(json.dumps(result, indent=2))