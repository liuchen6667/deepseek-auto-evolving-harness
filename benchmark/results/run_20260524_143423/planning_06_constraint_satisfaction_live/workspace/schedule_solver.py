#!/usr/bin/env python3
"""
会议安排约束满足问题求解器
"""
from itertools import product
import json

def time_to_minutes(time_str):
    """将HH:MM转换为分钟数"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def minutes_to_time(minutes):
    """将分钟数转换为HH:MM格式"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

# 会议定义
meetings = [
    {"id": 1, "name": "Product Review", "attendees": ["Alice", "Bob", "Carol"]},
    {"id": 2, "name": "Tech Design", "attendees": ["Bob", "David", "Eve"]},
    {"id": 3, "name": "Budget Planning", "attendees": ["Alice", "Frank", "Grace"]},
    {"id": 4, "name": "Team Sync", "attendees": ["Carol", "David", "Henry"]},
    {"id": 5, "name": "Client Demo", "attendees": ["Eve", "Frank", "Henry"]}
]

# 工作时间范围（9:00-18:00）
work_start = time_to_minutes("09:00")
work_end = time_to_minutes("18:00")
meeting_duration = 60  # 1小时
min_interval = 30  # 最小间隔30分钟

# Bob不可用时间（11:00-14:00）
bob_unavailable_start = time_to_minutes("11:00")
bob_unavailable_end = time_to_minutes("14:00")

def is_valid_schedule(schedule):
    """检查日程是否满足所有约束"""
    # 约束1：工作时间
    for meeting in schedule:
        start_time = meeting['start_minutes']
        end_time = start_time + meeting_duration
        if start_time < work_start or end_time > work_end:
            return False
    
    # 约束2：每个人同一时间只能参加一个会议
    all_attendees = {}
    for meeting in schedule:
        start_time = meeting['start_minutes']
        end_time = start_time + meeting_duration
        for attendee in meeting['attendees']:
            if attendee not in all_attendees:
                all_attendees[attendee] = []
            all_attendees[attendee].append((start_time, end_time))
    
    for attendee, times in all_attendees.items():
        times.sort()
        for i in range(len(times) - 1):
            if times[i][1] > times[i+1][0]:
                return False
    
    # 约束3：Alice必须在下午（14:00后）参加Product Review
    for meeting in schedule:
        if meeting['name'] == 'Product Review':
            if meeting['start_minutes'] < time_to_minutes("14:00"):
                return False
    
    # 约束4：Bob在11:00-14:00之间不可用
    for meeting in schedule:
        if 'Bob' in meeting['attendees']:
            start_time = meeting['start_minutes']
            end_time = start_time + meeting_duration
            # 检查会议是否与Bob不可用时间有重叠
            if not (end_time <= bob_unavailable_start or start_time >= bob_unavailable_end):
                return False
    
    # 约束5：Eve必须在上午（12:00前）参加Client Demo
    for meeting in schedule:
        if meeting['name'] == 'Client Demo':
            if meeting['start_minutes'] >= time_to_minutes("12:00"):
                return False
    
    # 约束6：Budget Planning必须在Tech Design之前
    budget_time = None
    tech_time = None
    for meeting in schedule:
        if meeting['name'] == 'Budget Planning':
            budget_time = meeting['start_minutes']
        elif meeting['name'] == 'Tech Design':
            tech_time = meeting['start_minutes']
    
    if budget_time is None or tech_time is None or budget_time >= tech_time:
        return False
    
    # 约束7：每个会议之间至少间隔30分钟
    meeting_times = [(m['start_minutes'], m['start_minutes'] + meeting_duration) for m in schedule]
    meeting_times.sort()
    
    for i in range(len(meeting_times) - 1):
        end_time_i = meeting_times[i][1]
        start_time_i1 = meeting_times[i+1][0]
        if start_time_i1 - end_time_i < min_interval:
            return False
    
    # 约束8：会议室只有2个，不能同时开3个会议
    # 检查任何时间点是否有超过2个会议同时进行
    timeline = []
    for start, end in meeting_times:
        timeline.append((start, 'start'))
        timeline.append((end, 'end'))
    
    timeline.sort()
    concurrent_meetings = 0
    for time, event in timeline:
        if event == 'start':
            concurrent_meetings += 1
        else:
            concurrent_meetings -= 1
        
        if concurrent_meetings > 2:
            return False
    
    return True

def assign_rooms(schedule):
    """为会议分配会议室"""
    # 按开始时间排序
    sorted_schedule = sorted(schedule, key=lambda x: x['start_minutes'])
    
    # 初始化会议室可用时间
    room_a_free = work_start
    room_b_free = work_start
    
    for meeting in sorted_schedule:
        start_time = meeting['start_minutes']
        
        # 分配会议室
        if room_a_free <= start_time:
            meeting['room'] = 'A'
            room_a_free = start_time + meeting_duration + min_interval
        elif room_b_free <= start_time:
            meeting['room'] = 'B'
            room_b_free = start_time + meeting_duration + min_interval
        else:
            # 如果没有可用会议室，调整时间
            meeting['room'] = 'A'
            meeting['start_minutes'] = min(room_a_free, room_b_free)
            room_a_free = meeting['start_minutes'] + meeting_duration + min_interval
    
    return schedule

def generate_schedule():
    """生成满足约束的日程安排"""
    # 可能的开始时间（以30分钟为间隔）
    possible_times = []
    current = work_start
    while current + meeting_duration <= work_end:
        possible_times.append(current)
        current += 30  # 30分钟间隔
    
    print(f"可能的时间点数量: {len(possible_times)}")
    
    # 尝试所有可能的时间组合
    for times in product(possible_times, repeat=5):
        schedule = []
        for i, (meeting, start_time) in enumerate(zip(meetings, times)):
            schedule.append({
                'id': meeting['id'],
                'name': meeting['name'],
                'attendees': meeting['attendees'],
                'start_minutes': start_time
            })
        
        if is_valid_schedule(schedule):
            print(f"找到有效日程!")
            # 分配会议室
            schedule = assign_rooms(schedule)
            return schedule
    
    return None

def format_schedule(schedule):
    """格式化日程为输出格式"""
    result = []
    for meeting in schedule:
        start_time = minutes_to_time(meeting['start_minutes'])
        end_time = minutes_to_time(meeting['start_minutes'] + meeting_duration)
        
        result.append({
            "meeting": meeting['name'],
            "start_time": start_time,
            "end_time": end_time,
            "room": meeting.get('room', 'A'),  # 默认会议室A
            "attendees": meeting['attendees']
        })
    
    return result

def main():
    print("开始寻找满足约束的会议安排...")
    
    schedule = generate_schedule()
    
    if schedule:
        print("\n找到解决方案:")
        formatted = format_schedule(schedule)
        for item in formatted:
            print(f"{item['meeting']}: {item['start_time']}-{item['end_time']} (会议室{item['room']}) - {', '.join(item['attendees'])}")
        
        # 保存到JSON文件
        with open('schedule.json', 'w') as f:
            json.dump(formatted, f, indent=2)
        print("\n日程已保存到 schedule.json")
    else:
        print("未找到满足所有约束的解决方案")

if __name__ == "__main__":
    main()