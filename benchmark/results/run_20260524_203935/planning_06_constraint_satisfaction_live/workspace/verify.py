import json
from datetime import datetime, timedelta

def time_to_minutes(t):
    """将时间字符串转换为分钟数（从0:00开始）"""
    dt = datetime.strptime(t, "%H:%M")
    return dt.hour * 60 + dt.minute

def load_schedule():
    with open('schedule.json', 'r') as f:
        return json.load(f)

def check_constraints(schedule):
    meetings = schedule['meetings']
    
    # 创建会议字典
    meeting_dict = {}
    for m in meetings:
        meeting_dict[m['name']] = m
    
    print("=== 检查约束条件 ===\n")
    
    all_passed = True
    
    # 1. 检查工作时间
    print("1. 工作时间检查 (9:00-18:00):")
    for m in meetings:
        start = time_to_minutes(m['start_time'])
        end = time_to_minutes(m['end_time'])
        if start < 9*60 or end > 18*60:
            print(f"  ❌ {m['name']}: {m['start_time']}-{m['end_time']} 超出工作时间")
            all_passed = False
        else:
            print(f"  ✓ {m['name']}: {m['start_time']}-{m['end_time']} 在工作时间内")
    
    # 2. 检查会议时长
    print("\n2. 会议时长检查 (1小时):")
    for m in meetings:
        start = time_to_minutes(m['start_time'])
        end = time_to_minutes(m['end_time'])
        if end - start != 60:
            print(f"  ❌ {m['name']}: 时长 {end-start} 分钟，不是1小时")
            all_passed = False
        else:
            print(f"  ✓ {m['name']}: 时长1小时")
    
    # 3. 检查人员冲突
    print("\n3. 人员冲突检查:")
    person_schedule = {}
    conflicts = []
    for m in meetings:
        start = time_to_minutes(m['start_time'])
        end = time_to_minutes(m['end_time'])
        for person in m['participants']:
            if person not in person_schedule:
                person_schedule[person] = []
            for (other_start, other_end, other_meeting) in person_schedule[person]:
                # 检查时间重叠
                if not (end <= other_start or start >= other_end):
                    conflicts.append(f"{person} 同时参加 {m['name']} ({m['start_time']}-{m['end_time']}) 和 {other_meeting} ({other_start//60}:{other_start%60:02d}-{other_end//60}:{other_end%60:02d})")
            person_schedule[person].append((start, end, m['name']))
    
    if conflicts:
        for conflict in conflicts:
            print(f"  ❌ {conflict}")
            all_passed = False
    else:
        print(f"  ✓ 无人员冲突")
    
    # 4. Alice必须在下午（14:00后）参加Product Review
    print("\n4. Alice在下午参加Product Review检查:")
    pr = meeting_dict.get('Product Review')
    if pr:
        start = time_to_minutes(pr['start_time'])
        if start >= 14*60:
            print(f"  ✓ Product Review 在 {pr['start_time']} 开始（14:00后）")
        else:
            print(f"  ❌ Product Review 在 {pr['start_time']} 开始（不是14:00后）")
            all_passed = False
    else:
        print("  ❌ 找不到Product Review会议")
        all_passed = False
    
    # 5. Bob在11:00-14:00之间不可用
    print("\n5. Bob在11:00-14:00之间不可用检查:")
    bob_meetings = []
    for m in meetings:
        if 'Bob' in m['participants']:
            start = time_to_minutes(m['start_time'])
            end = time_to_minutes(m['end_time'])
            bob_meetings.append((m['name'], start, end))
    
    bob_conflict = False
    for name, start, end in bob_meetings:
        # 检查会议是否与11:00-14:00有重叠
        if not (end <= 11*60 or start >= 14*60):
            print(f"  ❌ Bob参加 {name} ({start//60}:{start%60:02d}-{end//60}:{end%60:02d}) 与11:00-14:00冲突")
            bob_conflict = True
            all_passed = False
    
    if not bob_conflict:
        print(f"  ✓ Bob的会议都在11:00-14:00之外")
    
    # 6. Eve必须在上午（12:00前）参加Client Demo
    print("\n6. Eve在上午参加Client Demo检查:")
    cd = meeting_dict.get('Client Demo')
    if cd:
        start = time_to_minutes(cd['start_time'])
        if start < 12*60:
            print(f"  ✓ Client Demo 在 {cd['start_time']} 开始（12:00前）")
        else:
            print(f"  ❌ Client Demo 在 {cd['start_time']} 开始（不是12:00前）")
            all_passed = False
    else:
        print("  ❌ 找不到Client Demo会议")
        all_passed = False
    
    # 7. Budget Planning必须在Tech Design之前
    print("\n7. Budget Planning在Tech Design之前检查:")
    bp = meeting_dict.get('Budget Planning')
    td = meeting_dict.get('Tech Design')
    if bp and td:
        bp_start = time_to_minutes(bp['start_time'])
        td_start = time_to_minutes(td['start_time'])
        if bp_start < td_start:
            print(f"  ✓ Budget Planning ({bp['start_time']}) 在 Tech Design ({td['start_time']}) 之前")
        else:
            print(f"  ❌ Budget Planning ({bp['start_time']}) 不在 Tech Design ({td['start_time']}) 之前")
            all_passed = False
    else:
        print("  ❌ 找不到Budget Planning或Tech Design会议")
        all_passed = False
    
    # 8. 每个会议之间至少间隔30分钟
    print("\n8. 会议间隔检查（至少30分钟）:")
    # 按开始时间排序
    sorted_meetings = sorted(meetings, key=lambda x: time_to_minutes(x['start_time']))
    interval_ok = True
    for i in range(len(sorted_meetings)-1):
        m1 = sorted_meetings[i]
        m2 = sorted_meetings[i+1]
        m1_end = time_to_minutes(m1['end_time'])
        m2_start = time_to_minutes(m2['start_time'])
        interval = m2_start - m1_end
        if interval >= 30:
            print(f"  ✓ {m1['name']} 和 {m2['name']} 间隔 {interval} 分钟")
        else:
            print(f"  ❌ {m1['name']} 和 {m2['name']} 间隔 {interval} 分钟（小于30分钟）")
            interval_ok = False
            all_passed = False
    
    # 9. 会议室只有2个，不能同时开3个会议
    print("\n9. 会议室冲突检查（最多2个同时会议）:")
    # 创建时间线
    timeline = {}
    for m in meetings:
        start = time_to_minutes(m['start_time'])
        end = time_to_minutes(m['end_time'])
        # 每半小时检查一次
        for t in range(start, end, 30):
            if t not in timeline:
                timeline[t] = []
            timeline[t].append(m['name'])
    
    room_conflict = False
    for t, meetings_at_t in timeline.items():
        if len(meetings_at_t) > 2:
            hour = t // 60
            minute = t % 60
            print(f"  ❌ {hour}:{minute:02d} 时有 {len(meetings_at_t)} 个会议同时进行: {meetings_at_t}")
            room_conflict = True
            all_passed = False
    
    if not room_conflict:
        print(f"  ✓ 任何时间点最多2个会议同时进行")
    
    print(f"\n=== 总体结果: {'所有约束都满足！' if all_passed else '有约束未满足！'} ===")
    
    return all_passed

if __name__ == "__main__":
    schedule = load_schedule()
    check_constraints(schedule)