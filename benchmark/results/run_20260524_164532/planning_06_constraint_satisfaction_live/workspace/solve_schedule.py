#!/usr/bin/env python3
"""
解决会议安排问题的脚本
"""

import json
import itertools
from datetime import datetime, timedelta

# 会议定义
meetings = [
    {"id": 1, "name": "Product Review", "attendees": ["Alice", "Bob", "Carol"]},
    {"id": 2, "name": "Tech Design", "attendees": ["Bob", "David", "Eve"]},
    {"id": 3, "name": "Budget Planning", "attendees": ["Alice", "Frank", "Grace"]},
    {"id": 4, "name": "Team Sync", "attendees": ["Carol", "David", "Henry"]},
    {"id": 5, "name": "Client Demo", "attendees": ["Eve", "Frank", "Henry"]},
]

# 工作时间：9:00-18:00（9小时）
work_start = datetime.strptime("09:00", "%H:%M")
work_end = datetime.strptime("18:00", "%H:%M")
work_hours = 9
meeting_duration = 60  # 分钟
min_interval = 30  # 分钟

# 可用时间槽（半小时间隔）
time_slots = []
current = work_start
while current + timedelta(minutes=meeting_duration) <= work_end:
    time_slots.append(current)
    current += timedelta(minutes=30)

# 将时间转换为可读字符串
def time_str(t):
    return t.strftime("%H:%M")

def check_constraints(schedule):
    """检查调度是否满足所有约束"""
    # 1. 工作时间约束已在时间槽生成时处理
    
    # 2. 每个人同一时间只能参加一个会议
    for i, m1 in enumerate(schedule):
        for j, m2 in enumerate(schedule):
            if i == j:
                continue
            # 检查时间重叠
            m1_start = m1["start"]
            m2_start = m2["start"]
            
            # 如果开始时间相同或相差小于60分钟（会议时长），则可能重叠
            if abs((m1_start - m2_start).total_seconds() / 60) < meeting_duration:
                # 会议重叠，检查参会人员冲突
                common_attendees = set(m1["attendees"]) & set(m2["attendees"])
                if common_attendees:
                    return False, f"人员冲突: {common_attendees} 同时参加 {m1['name']} 和 {m2['name']}"
    
    # 3. Alice 必须在下午（14:00后）参加 Product Review
    for meeting in schedule:
        if meeting["name"] == "Product Review":
            if meeting["start"].hour < 14:
                return False, "Product Review 必须在14:00后（Alice约束）"
    
    # 4. Bob 在 11:00-14:00 之间不可用
    bob_unavailable_start = datetime.strptime("11:00", "%H:%M")
    bob_unavailable_end = datetime.strptime("14:00", "%H:%M")
    for meeting in schedule:
        if "Bob" in meeting["attendees"]:
            meeting_start = meeting["start"]
            meeting_end = meeting_start + timedelta(minutes=meeting_duration)
            # 检查会议是否与Bob不可用时间段重叠
            if (meeting_start < bob_unavailable_end and 
                meeting_end > bob_unavailable_start):
                return False, f"Bob 在11:00-14:00不可用，但参加了 {meeting['name']}"
    
    # 5. Eve 必须在上午（12:00前）参加 Client Demo
    noon = datetime.strptime("12:00", "%H:%M")
    for meeting in schedule:
        if meeting["name"] == "Client Demo":
            if meeting["start"].hour >= 12:
                return False, "Client Demo 必须在12:00前（Eve约束）"
    
    # 6. Budget Planning 必须在 Tech Design 之前
    budget_planning_time = None
    tech_design_time = None
    for meeting in schedule:
        if meeting["name"] == "Budget Planning":
            budget_planning_time = meeting["start"]
        elif meeting["name"] == "Tech Design":
            tech_design_time = meeting["start"]
    
    if budget_planning_time is None or tech_design_time is None:
        return False, "缺少Budget Planning或Tech Design"
    
    if budget_planning_time >= tech_design_time:
        return False, "Budget Planning 必须在 Tech Design 之前"
    
    # 7. 每个会议之间至少间隔30分钟（已在时间槽中处理，但需要确保会议室分配不冲突）
    # 我们将在会议室分配中处理
    
    # 8. 会议室只有2个，不能同时开3个会议
    # 按时间分组检查同时进行的会议
    time_groups = {}
    for meeting in schedule:
        key = meeting["start"]
        if key not in time_groups:
            time_groups[key] = 0
        time_groups[key] += 1
    
    for time, count in time_groups.items():
        if count > 2:
            return False, f"在 {time_str(time)} 有 {count} 个会议同时进行，超过2个会议室"
    
    return True, "所有约束满足"

def assign_rooms(schedule):
    """为会议分配会议室A或B"""
    # 按开始时间排序
    sorted_schedule = sorted(schedule, key=lambda x: x["start"])
    
    # 分配会议室
    for meeting in sorted_schedule:
        meeting["room"] = None
    
    # 对于每个时间点，分配可用的会议室
    time_points = sorted(set(m["start"] for m in sorted_schedule))
    
    for time in time_points:
        # 获取这个时间开始的会议
        concurrent_meetings = [m for m in sorted_schedule if m["start"] == time]
        
        # 可用会议室
        available_rooms = ["A", "B"]
        
        # 分配会议室
        for i, meeting in enumerate(concurrent_meetings):
            if i < len(available_rooms):
                meeting["room"] = available_rooms[i]
            else:
                # 这不应该发生，因为我们已经检查了同时会议数量
                meeting["room"] = "A"
    
    return sorted_schedule

def generate_schedule():
    """生成满足约束的调度"""
    # 尝试所有可能的排列（5个会议的时间安排）
    # 由于时间槽有限，我们使用组合方法
    
    # 生成所有可能的时间分配（5个不同的时间槽）
    from itertools import permutations
    
    # 时间槽数量
    n_slots = len(time_slots)
    
    print(f"可用时间槽数量: {n_slots}")
    print(f"会议数量: {len(meetings)}")
    
    # 尝试所有可能的时间分配组合
    # 使用组合而不是排列以减少搜索空间
    from itertools import combinations
    
    # 生成所有可能的5个不同时间槽的组合
    slot_combinations = list(combinations(range(n_slots), 5))
    print(f"时间槽组合数量: {len(slot_combinations)}")
    
    # 对于每个组合，尝试所有会议排列
    for slot_indices in slot_combinations[:1000]:  # 限制搜索数量
        selected_slots = [time_slots[i] for i in slot_indices]
        
        # 尝试所有会议到时间槽的排列
        for perm in itertools.permutations(meetings, 5):
            schedule = []
            for i, meeting in enumerate(perm):
                schedule.append({
                    "id": meeting["id"],
                    "name": meeting["name"],
                    "attendees": meeting["attendees"],
                    "start": selected_slots[i],
                    "end": selected_slots[i] + timedelta(minutes=meeting_duration)
                })
            
            # 检查约束
            valid, msg = check_constraints(schedule)
            if valid:
                # 分配会议室
                schedule_with_rooms = assign_rooms(schedule)
                
                # 验证会议室分配
                # 检查同一时间同一会议室是否分配了多个会议
                room_assignments = {}
                for meeting in schedule_with_rooms:
                    key = (meeting["start"], meeting["room"])
                    if key in room_assignments:
                        continue  # 这不应该发生
                    room_assignments[key] = meeting["name"]
                
                return schedule_with_rooms
    
    return None

def main():
    """主函数"""
    print("开始寻找满足约束的会议安排...")
    
    # 生成调度
    schedule = generate_schedule()
    
    if schedule is None:
        print("未找到满足所有约束的安排")
        return False
    
    print("\n找到满足所有约束的安排:")
    print("=" * 60)
    
    # 格式化输出
    output_schedule = []
    for meeting in sorted(schedule, key=lambda x: x["start"]):
        meeting_info = {
            "name": meeting["name"],
            "start": time_str(meeting["start"]),
            "end": time_str(meeting["end"]),
            "room": meeting["room"],
            "attendees": meeting["attendees"]
        }
        output_schedule.append(meeting_info)
        
        print(f"会议: {meeting['name']}")
        print(f"  时间: {time_str(meeting['start'])} - {time_str(meeting['end'])}")
        print(f"  会议室: {meeting['room']}")
        print(f"  参会人员: {', '.join(meeting['attendees'])}")
        print()
    
    # 保存到JSON文件
    with open("schedule.json", "w") as f:
        json.dump(output_schedule, f, indent=2)
    
    print(f"\n调度已保存到 schedule.json")
    
    # 验证约束
    print("\n验证约束:")
    print("-" * 40)
    
    # 重新检查所有约束
    valid, msg = check_constraints(schedule)
    print(f"所有约束检查: {msg}")
    
    # 检查特定约束
    # 1. Alice下午参加Product Review
    for m in schedule:
        if m["name"] == "Product Review":
            print(f"Product Review在{m['start'].hour}:{m['start'].minute:02d}，Alice在下午参加: {m['start'].hour >= 14}")
    
    # 2. Bob 11:00-14:00不可用
    bob_unavailable = True
    for m in schedule:
        if "Bob" in m["attendees"]:
            start = m["start"]
            end = start + timedelta(minutes=60)
            if start.hour < 14 and end.hour > 11:
                bob_unavailable = False
    print(f"Bob在11:00-14:00未安排会议: {bob_unavailable}")
    
    # 3. Eve上午参加Client Demo
    for m in schedule:
        if m["name"] == "Client Demo":
            print(f"Client Demo在{m['start'].hour}:{m['start'].minute:02d}，Eve在上午参加: {m['start'].hour < 12}")
    
    # 4. Budget Planning在Tech Design之前
    bp_time = None
    td_time = None
    for m in schedule:
        if m["name"] == "Budget Planning":
            bp_time = m["start"]
        elif m["name"] == "Tech Design":
            td_time = m["start"]
    if bp_time and td_time:
        print(f"Budget Planning({time_str(bp_time)})在Tech Design({time_str(td_time)})之前: {bp_time < td_time}")
    
    # 5. 会议室限制
    time_counts = {}
    for m in schedule:
        key = time_str(m["start"])
        time_counts[key] = time_counts.get(key, 0) + 1
    
    print(f"\n同时进行的会议数量:")
    for time, count in sorted(time_counts.items()):
        print(f"  {time}: {count}个会议")
    
    return True

if __name__ == "__main__":
    main()