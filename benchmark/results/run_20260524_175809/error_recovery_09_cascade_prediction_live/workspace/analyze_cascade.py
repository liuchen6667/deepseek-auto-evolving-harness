#!/usr/bin/env python3

# 依赖关系
# X -> Y 表示 X 依赖 Y
# 如果 Y 不可用或降级，X 会受影响
dependencies = {
    'A': ['B', 'C'],  # A -> B, A -> C
    'B': ['D'],       # B -> D
    'C': ['E'],       # C -> E
    'F': ['D'],       # F -> D
    'G': ['E'],       # G -> E
    'H': ['E']        # H -> E
}

# 维护计划
maintenance = {
    'D': 'down',      # 完全停机
    'E': 'degraded'   # 降级到50%性能
}

# 所有服务
all_services = set(dependencies.keys())
for deps in dependencies.values():
    all_services.update(deps)
all_services = sorted(all_services)
print(f"所有服务: {all_services}")

# 找出直接影响（直接依赖 D 或 E 的服务）
direct_impacts = []
for service, deps in dependencies.items():
    if 'D' in deps or 'E' in deps:
        direct_impacts.append(service)

direct_impacts = sorted(direct_impacts)
print(f"直接影响服务: {direct_impacts}")

# 找出间接影响（依赖已受影响服务的服务）
# 使用BFS遍历依赖图
affected = set(direct_impacts)
changed = True
while changed:
    changed = False
    for service, deps in dependencies.items():
        if service not in affected:
            # 检查是否依赖任何已受影响的服务
            for dep in deps:
                if dep in affected:
                    affected.add(service)
                    changed = True
                    break

indirect_impacts = sorted([s for s in affected if s not in direct_impacts])
print(f"间接影响服务: {indirect_impacts}")

# 计算风险等级
risk_levels = {}
for service in all_services:
    if service in ['D', 'E']:
        continue  # D和E是维护对象，不计算风险
    
    if service in dependencies:
        deps = dependencies[service]
        
        # 检查是否依赖停机服务D
        if 'D' in deps:
            risk_levels[service] = 'high'
            continue
        
        # 检查是否同时依赖两个已受影响上游
        affected_deps = [dep for dep in deps if dep in affected]
        if len(affected_deps) >= 2:
            risk_levels[service] = 'high'
            continue
        
        # 检查是否只依赖降级服务E
        if 'E' in deps and len(deps) == 1:
            risk_levels[service] = 'medium'
            continue
        
        # 检查是否只通过单条间接链路受到影响
        if service in indirect_impacts:
            risk_levels[service] = 'low'
    else:
        # 服务没有依赖其他服务（如D、E本身）
        pass

print(f"风险等级: {risk_levels}")

# 计算恢复优先级
recovery_priority = []

# 1. 先恢复造成影响范围更大的根因服务
# 计算每个维护服务的影响范围
impact_counts = {}
for service in ['D', 'E']:
    count = 0
    for s in all_services:
        if s in dependencies:
            if service in dependencies[s]:
                count += 1
    impact_counts[service] = count

print(f"影响范围统计: {impact_counts}")

# D影响B和F，E影响C、G、H
# D影响2个直接服务，E影响3个直接服务
# 但根据规则：先恢复造成影响范围更大的根因服务
# 让我们分析完整影响链：
# D -> B -> A (间接)
# D -> F (直接)
# E -> C -> A (间接)
# E -> G (直接)
# E -> H (直接)

# D的完整影响：B, F, A (通过B)
# E的完整影响：C, G, H, A (通过C)
# D影响3个服务，E影响4个服务，所以先恢复E？
# 但D是完全停机，E是降级，可能D的影响更严重

# 根据规则：先恢复造成影响范围更大的根因服务
# 让我们按照影响的服务数量排序
recovery_priority.append('E')  # E影响更多服务
recovery_priority.append('D')  # 然后D

# 2. 再恢复直接受影响服务
direct_affected = []
for service in direct_impacts:
    if service not in recovery_priority:
        direct_affected.append(service)

# 按字母排序
recovery_priority.extend(sorted(direct_affected))

# 3. 最后恢复间接受影响服务
for service in indirect_impacts:
    if service not in recovery_priority:
        recovery_priority.append(service)

print(f"恢复优先级: {recovery_priority}")

# 生成notes
notes = [
    "关键传播链路1: D停机直接影响B和F，B故障进一步导致A间接受影响",
    "关键传播链路2: E降级直接影响C、G和H，C性能下降进一步导致A间接受影响",
    "缓解思路: 考虑在维护期间为A提供备用方案，因为A同时依赖B和C，面临高风险",
    "缓解思路: 对于只依赖E的服务(G、H)，可接受50%性能降级，风险中等"
]

# 输出结果
result = {
    "direct_impacts": direct_impacts,
    "indirect_impacts": indirect_impacts,
    "risk_levels": risk_levels,
    "recovery_priority": recovery_priority,
    "notes": notes[:2]  # 只取前2条
}

import json
with open('cascade_prediction.json', 'w') as f:
    json.dump(result, f, indent=2)

print("\n结果已保存到 cascade_prediction.json")
print(json.dumps(result, indent=2))
