import json
from datetime import datetime, timedelta

def parse_time(time_str):
    return datetime.strptime(time_str, "%H:%M")

def check_constraints(schedule):
    meetings = schedule["meetings"]
    
    # 1. 检查工作时间 (9:00-18:00)
    work_start = parse_time("09:00")
    work_end = parse_time("18:00")
    
    for meeting in meetings:
        start = parse_time(meeting["start_time"])
        end = parse_time(meeting["end_time"])
        if start < work_start or end > work_end:
            print(f"❌ {meeting['name']}: 不在工作时间内 ({meeting['start_time']}-{meeting['end_time']})")
            return False
        
        # 检查会议时长是否为1小时
        duration = end - start
        if duration != timedelta(hours=1):
            print(f"❌ {meeting['name']}: 会议时长不是1小时 ({duration})")
            return False
    
    print("✓ 所有会议在工作时间内且为1小时")
    
    # 2. 检查人员冲突
    person_schedule = {}
    for meeting in meetings:
        start = parse_time(meeting["start_time"])
        end = parse_time(meeting["end_time"])
        for person in meeting["participants"]:
            if person not in person_schedule:
                person_schedule[person] = []
            
            # 检查是否有时间重叠
            for (s, e) in person_schedule[person]:
                if not (end <= s or start >= e):
                    print(f"❌ {person} 在 {meeting['name']} ({start.time()}-{end.time()}) 与另一个会议 ({s.time()}-{e.time()}) 冲突")
                    return False
            
            person_schedule[person].append((start, end))
    
    print("✓ 无人员冲突")
    
    # 3. Alice必须在下午（14:00后）参加Product Review
    alice_product_review = None
    for meeting in meetings:
        if meeting["name"] == "Product Review" and "Alice" in meeting["participants"]:
            alice_product_review = meeting
            break
    
    if alice_product_review:
        start = parse_time(alice_product_review["start_time"])
        if start >= parse_time("14:00"):
            print(f"✓ Alice在下午参加Product Review ({alice_product_review['start_time']})")
        else:
            print(f"❌ Alice不在下午参加Product Review ({alice_product_review['start_time']})")
            return False
    else:
        print("❌ Alice没有参加Product Review")
        return False
    
    # 4. Bob在11:00-14:00之间不可用
    bob_ok = True
    for meeting in meetings:
        if "Bob" in meeting["participants"]:
            start = parse_time(meeting["start_time"])
            end = parse_time(meeting["end_time"])
            unavailable_start = parse_time("11:00")
            unavailable_end = parse_time("14:00")
            
            # 检查会议是否与不可用时间重叠
            if not (end <= unavailable_start or start >= unavailable_end):
                print(f"❌ Bob在不可用时间(11:00-14:00)参加了{meeting['name']} ({meeting['start_time']}-{meeting['end_time']})")
                bob_ok = False
    
    if bob_ok:
        print("✓ Bob在11:00-14:00之间没有会议")
    else:
        return False
    
    # 5. Eve必须在上午（12:00前）参加Client Demo
    eve_client_demo = None
    for meeting in meetings:
        if meeting["name"] == "Client Demo" and "Eve" in meeting["participants"]:
            eve_client_demo = meeting
            break
    
    if eve_client_demo:
        start = parse_time(eve_client_demo["start_time"])
        if start < parse_time("12:00"):
            print(f"✓ Eve在上午参加Client Demo ({eve_client_demo['start_time']})")
        else:
            print(f"❌ Eve不在上午参加Client Demo ({eve_client_demo['start_time']})")
            return False
    else:
        print("❌ Eve没有参加Client Demo")
        return False
    
    # 6. Budget Planning必须在Tech Design之前
    budget_time = None
    tech_time = None
    
    for meeting in meetings:
        if meeting["name"] == "Budget Planning":
            budget_time = parse_time(meeting["start_time"])
        if meeting["name"] == "Tech Design":
            tech_time = parse_time(meeting["start_time"])
    
    if budget_time and tech_time:
        if budget_time < tech_time:
            print(f"✓ Budget Planning({budget_time.time()})在Tech Design({tech_time.time()})之前")
        else:
            print(f"❌ Budget Planning不在Tech Design之前")
            return False
    else:
        print("❌ 缺少Budget Planning或Tech Design")
        return False
    
    # 7. 每个会议之间至少间隔30分钟
    # 按开始时间排序
    sorted_meetings = sorted(meetings, key=lambda x: parse_time(x["start_time"]))
    
    for i in range(len(sorted_meetings) - 1):
        current_end = parse_time(sorted_meetings[i]["end_time"])
        next_start = parse_time(sorted_meetings[i+1]["start_time"])
        
        gap = (next_start - current_end).total_seconds() / 60  # 分钟
        
        if gap >= 30:
            print(f"✓ {sorted_meetings[i]['name']} 和 {sorted_meetings[i+1]['name']} 间隔{gap}分钟")
        else:
            print(f"❌ {sorted_meetings[i]['name']} 和 {sorted_meetings[i+1]['name']} 间隔只有{gap}分钟，不足30分钟")
            return False
    
    # 8. 会议室只有2个，不能同时开3个会议
    # 按时间检查并发会议数
    time_points = []
    for meeting in meetings:
        start = parse_time(meeting["start_time"])
        end = parse_time(meeting["end_time"])
        time_points.append((start, "start"))
        time_points.append((end, "end"))
    
    time_points.sort()
    
    concurrent_meetings = 0
    max_concurrent = 0
    
    for time_point, event_type in time_points:
        if event_type == "start":
            concurrent_meetings += 1
            max_concurrent = max(max_concurrent, concurrent_meetings)
        else:
            concurrent_meetings -= 1
    
    if max_concurrent <= 2:
        print(f"✓ 最多同时有{max_concurrent}个会议，不超过2个会议室")
    else:
        print(f"❌ 同时有{max_concurrent}个会议，超过2个会议室")
        return False
    
    print("\n✅ 所有约束条件满足！")
    return True

if __name__ == "__main__":
    with open("schedule.json", "r") as f:
        schedule = json.load(f)
    
    print("验证会议安排约束条件:\n")
    success = check_constraints(schedule)
    
    if not success:
        print("\n❌ 安排不符合约束条件")
        exit(1)