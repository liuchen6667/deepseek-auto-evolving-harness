#!/usr/bin/env python3

# 依赖关系：X -> Y 表示 X 依赖 Y
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
    'D': '停机',  # 完全停机
    'E': '降级'   # 降级到50%性能
}

# 受影响服务集合
affected = set()

# 步骤1：直接影响（直接依赖D或E的服务）
direct_impacts = []
for service, deps in dependencies.items():
    if 'D' in deps or 'E' in deps:
        direct_impacts.append(service)
        affected.add(service)

# 步骤2：间接影响（依赖"已受影响服务"的服务）
# 我们需要递归地传播影响
def propagate_impact(affected_set):
    new_affected = set()
    for service, deps in dependencies.items():
        if service in affected_set:
            continue  # 已经是受影响服务
        # 检查是否依赖任何受影响的服务
        for dep in deps:
            if dep in affected_set:
                new_affected.add(service)
                break
    return new_affected

# 持续传播直到没有新受影响的服务
while True:
    new_affected = propagate_impact(affected)
    if not new_affected:
        break
    affected.update(new_affected)

# 间接影响 = 所有受影响服务 - 直接影响
indirect_impacts = [s for s in affected if s not in direct_impacts]

# 步骤3：风险等级计算
risk_levels = {}

for service in affected:
    deps = dependencies.get(service, [])
    
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
    # 对于间接影响的服务，检查它们是否只通过一条路径受到影响
    if service in indirect_impacts:
        # 简单的检查：如果只有一个上游依赖是受影响的
        if len(affected_deps) == 1:
            risk_levels[service] = 'low'
        else:
            # 多个受影响上游，但都不是D，且E只是降级
            # 根据规则，同时依赖两个已受影响上游是high，所以这里应该是low或medium
            risk_levels[service] = 'low'
    else:
        # 直接影响但不是high或medium的情况
        risk_levels[service] = 'low'

# 步骤4：恢复优先级
# 规则：
# 1. 先恢复造成影响范围更大的根因服务（D和E）
# 2. 再恢复直接受影响服务
# 3. 最后恢复间接受影响服务

# 计算每个服务的影响范围（下游依赖链长度）
def calculate_impact_scope(service, visited=None):
    if visited is None:
        visited = set()
    
    if service in visited:
        return 0
    
    visited.add(service)
    
    # 查找所有依赖此服务的服务
    downstream = 0
    for s, deps in dependencies.items():
        if service in deps:
            downstream += 1 + calculate_impact_scope(s, visited.copy())
    
    return downstream

impact_scopes = {}
for service in ['D', 'E'] + direct_impacts + indirect_impacts:
    if service not in impact_scopes:
        impact_scopes[service] = calculate_impact_scope(service)

# 恢复优先级顺序
recovery_priority = []

# 1. 根因服务按影响范围排序
root_causes = ['D', 'E']
root_causes.sort(key=lambda x: impact_scopes[x], reverse=True)
recovery_priority.extend(root_causes)

# 2. 直接受影响服务按影响范围排序
direct_sorted = sorted([s for s in direct_impacts if s not in root_causes], 
                      key=lambda x: impact_scopes[x], reverse=True)
recovery_priority.extend(direct_sorted)

# 3. 间接受影响服务按影响范围排序
indirect_sorted = sorted(indirect_impacts, key=lambda x: impact_scopes[x], reverse=True)
recovery_priority.extend(indirect_sorted)

# 去重并确保所有受影响服务都在列表中
final_priority = []
seen = set()
for service in recovery_priority:
    if service not in seen:
        final_priority.append(service)
        seen.add(service)

# 添加可能缺失的受影响服务
for service in affected:
    if service not in seen:
        final_priority.append(service)
        seen.add(service)

# 步骤5：生成输出
output = {
    "direct_impacts": sorted(direct_impacts),
    "indirect_impacts": sorted(indirect_impacts),
    "risk_levels": {k: risk_levels[k] for k in sorted(risk_levels.keys())},
    "recovery_priority": final_priority,
    "notes": [
        "关键传播链路：D停机影响B和F（直接影响），进而影响A（间接影响）；E降级影响C、G、H（直接影响），进而影响A（间接影响）",
        "缓解思路：1) 考虑将A的部分功能切换到备用路径避免B/C同时受影响；2) 对G和H实施流量限流以应对E的性能降级"
    ]
}

# 打印结果
import json
print(json.dumps(output, indent=2))

# 保存到文件
with open('cascade_prediction.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\n结果已保存到 cascade_prediction.json")