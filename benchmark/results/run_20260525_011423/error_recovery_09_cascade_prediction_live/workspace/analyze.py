# 分析级联故障预测
dependencies = {
    'A': ['B', 'C'],
    'B': ['D'],
    'C': ['E'],
    'F': ['D'],
    'G': ['E'],
    'H': ['E']
}

# 维护影响
maintenance = {
    'D': 'down',  # 完全停机
    'E': 'degraded'  # 降级到50%
}

# 找到所有服务
all_services = set()
for service, deps in dependencies.items():
    all_services.add(service)
    all_services.update(deps)

print("所有服务:", sorted(all_services))
print("\n依赖关系:")
for service, deps in dependencies.items():
    print(f"{service} -> {deps}")

print("\n维护影响:")
for service, status in maintenance.items():
    print(f"{service}: {status}")

# 计算直接影响
direct_impacts = set()
for service, deps in dependencies.items():
    if 'D' in deps or 'E' in deps:
        direct_impacts.add(service)

print(f"\n直接影响服务: {sorted(direct_impacts)}")

# 计算间接影响
indirect_impacts = set()

# 递归查找间接影响
def find_indirect_impacts(affected_services):
    new_impacts = set()
    for service, deps in dependencies.items():
        if service in affected_services or service in maintenance:
            continue  # 已经是受影响或维护中的服务
        # 检查是否依赖已受影响的服务
        for dep in deps:
            if dep in affected_services or dep in maintenance:
                new_impacts.add(service)
                break
    return new_impacts

# 初始受影响集合：维护的服务 + 直接影响
affected = set(maintenance.keys()) | direct_impacts
print(f"\n初始受影响集合: {sorted(affected)}")

# 迭代查找间接影响
while True:
    new_impacts = find_indirect_impacts(affected)
    if not new_impacts:
        break
    indirect_impacts.update(new_impacts)
    affected.update(new_impacts)

print(f"\n间接影响服务: {sorted(indirect_impacts)}")

# 计算风险等级
risk_levels = {}
all_impacted = direct_impacts | indirect_impacts

for service in all_impacted:
    deps = dependencies.get(service, [])
    
    # 检查是否依赖停机服务D
    depends_on_down = False
    # 递归检查依赖链
    def check_depends_on_down(svc, visited=None):
        if visited is None:
            visited = set()
        if svc in visited:
            return False
        visited.add(svc)
        
        if svc == 'D':
            return True
        if svc not in dependencies:
            return False
        
        for dep in dependencies[svc]:
            if check_depends_on_down(dep, visited):
                return True
        return False
    
    depends_on_down = check_depends_on_down(service)
    
    # 计算依赖的已受影响上游数量
    affected_upstream_count = 0
    for dep in deps:
        if dep in all_impacted or dep in maintenance:
            affected_upstream_count += 1
    
    # 确定风险等级
    if depends_on_down or affected_upstream_count >= 2:
        risk_levels[service] = 'high'
    elif 'E' in deps and not depends_on_down and affected_upstream_count == 1:
        risk_levels[service] = 'medium'
    else:
        risk_levels[service] = 'low'

print(f"\n风险等级: {risk_levels}")

# 计算恢复优先级
# 根据规则：先恢复造成影响范围更大的根因服务
# 再恢复直接受影响服务，最后恢复间接受影响服务

recovery_priority = []

# 根因服务：D和E（维护的服务）
root_causes = ['D', 'E']

# 按影响范围排序：先恢复影响更大的
# D的影响链：D -> B, F; B -> A
# E的影响链：E -> C, G, H; C -> A

# 计算每个根因的影响范围
impact_counts = {}
for root in root_causes:
    count = 0
    for service in all_impacted:
        # 检查service是否依赖root
        def depends_on_root(svc, target, visited=None):
            if visited is None:
                visited = set()
            if svc in visited:
                return False
            visited.add(svc)
            
            if svc == target:
                return True
            if svc not in dependencies:
                return False
            
            for dep in dependencies[svc]:
                if depends_on_root(dep, target, visited):
                    return True
            return False
        
        if depends_on_root(service, root):
            count += 1
    
    impact_counts[root] = count

print(f"\n根因影响范围: {impact_counts}")

# 先恢复影响范围更大的（D影响B,F,A；E影响C,G,H,A）
# D影响3个服务（B,F,A），E影响4个服务（C,G,H,A），所以先恢复E
if impact_counts.get('E', 0) >= impact_counts.get('D', 0):
    recovery_priority.append('E')
    recovery_priority.append('D')
else:
    recovery_priority.append('D')
    recovery_priority.append('E')

# 直接受影响服务
direct_sorted = sorted(direct_impacts)
recovery_priority.extend(direct_sorted)

# 间接受影响服务
indirect_sorted = sorted(indirect_impacts)
recovery_priority.extend(indirect_sorted)

print(f"\n恢复优先级: {recovery_priority}")

# 生成最终输出
result = {
    "direct_impacts": sorted(direct_impacts),
    "indirect_impacts": sorted(indirect_impacts),
    "risk_levels": risk_levels,
    "recovery_priority": recovery_priority,
    "notes": [
        "关键传播链路1：D停机直接影响B和F，间接影响A（通过B）",
        "关键传播链路2：E降级直接影响C、G、H，间接影响A（通过C）",
        "缓解思路：考虑在维护期间为A提供降级服务，因为它依赖B和C两个受影响上游",
        "注意：A同时受到D和E维护的双重影响，风险等级为high"
    ]
}

print("\n最终结果:")
import json
print(json.dumps(result, indent=2))
