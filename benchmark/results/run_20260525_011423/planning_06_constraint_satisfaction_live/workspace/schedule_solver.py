#!/usr/bin/env python3
"""
会议安排约束满足问题求解器
"""

from itertools import combinations
import json

def main():
    # 定义会议
    meetings = [
        {"id": 1, "name": "Product Review", "participants": ["Alice", "Bob", "Carol"], "duration": 1},
        {"id": 2, "name": "Tech Design", "participants": ["Bob", "David", "Eve"], "duration": 1},
        {"id": 3, "name": "Budget Planning", "participants": ["Alice", "Frank", "Grace"], "duration": 1},
        {"id": 4, "name": "Team Sync", "participants": ["Carol", "David", "Henry"], "duration": 1},
        {"id": 5, "name": "Client Demo", "participants": ["Eve", "Frank", "Henry"], "duration": 1},
    ]
    
    # 工作时间：9:00-18:00（9小时），每30分钟一个时间段
    time_slots = []
    for hour in range(9, 18):
        for minute in [0, 30]:
            if hour == 17 and minute == 30:  # 17:30开始的话会议会到18:30，超出工作时间
                continue
            time_slots.append(f"{hour:02d}:{minute:02d}")
    
    # 会议室
    rooms = ["A", "B"]
    
    # 尝试所有可能的安排
    from itertools import product
    
    # 为每个会议分配时间（以30分钟为单位的时间索引）和房间
    def time_to_minutes(t):
        hour, minute = map(int, t.split(":"))
        return hour * 60 + minute
    
    def minutes_to_time(m):
        return f"{m//60:02d}:{m%60:02d}"
    
    # 生成所有可能的时间安排（每个会议开始时间）
    possible_times = []
    for i in range(len(time_slots) - 1):  # -1 因为会议需要1小时（2个30分钟时段）
        start_time = time_slots[i]
        end_time_minutes = time_to_minutes(start_time) + 60
        if end_time_minutes <= 18 * 60:  # 确保在18:00前结束
            possible_times.append(start_time)
    
    print(f"工作时间段: {time_slots}")
    print(f"可能的会议开始时间: {possible_times}")
    
    # 尝试所有可能的组合
    from itertools import permutations
    
    solutions = []
    
    # 由于搜索空间较大，我们使用启发式方法
    # 首先尝试满足硬约束
    
    # 约束 3: Alice 必须在下午（14:00 后）参加 Product Review
    # 约束 5: Eve 必须在上午（12:00 前）参加 Client Demo
    # 约束 6: Budget Planning 必须在 Tech Design 之前
    
    # 生成所有可能的会议时间排列
    meeting_ids = [1, 2, 3, 4, 5]
    
    # 限制搜索空间
    for start1 in possible_times:
        for start2 in possible_times:
            for start3 in possible_times:
                for start4 in possible_times:
                    for start5 in possible_times:
                        starts = [start1, start2, start3, start4, start5]
                        
                        # 检查基本约束：会议时间不重叠（考虑30分钟间隔）
                        valid = True
                        for i in range(5):
                            for j in range(i+1, 5):
                                t1 = time_to_minutes(starts[i])
                                t2 = time_to_minutes(starts[j])
                                if abs(t1 - t2) < 90:  # 1小时会议 + 30分钟间隔 = 90分钟
                                    valid = False
                                    break
                            if not valid:
                                break
                        
                        if not valid:
                            continue
                        
                        # 检查会议室约束（最多2个同时会议）
                        # 由于我们已经确保会议间隔至少90分钟，所以不会同时有超过2个会议
                        # 但还需要检查是否有3个会议在重叠的时间段
                        timeline = []
                        for i, start in enumerate(starts):
                            start_min = time_to_minutes(start)
                            end_min = start_min + 60
                            timeline.append((start_min, end_min, i+1))
                        
                        # 按时间排序
                        timeline.sort()
                        
                        # 检查任意时间点是否有超过2个会议同时进行
                        max_concurrent = 0
                        for time_point in range(9*60, 18*60, 5):  # 每5分钟检查一次
                            concurrent = 0
                            for start, end, _ in timeline:
                                if start <= time_point < end:
                                    concurrent += 1
                            max_concurrent = max(max_concurrent, concurrent)
                        
                        if max_concurrent > 2:
                            continue
                        
                        # 检查约束 3: Product Review (会议1) 必须在14:00后（Alice参加）
                        if time_to_minutes(starts[0]) < 14 * 60:
                            # 会议1是Product Review
                            continue
                        
                        # 检查约束 5: Client Demo (会议5) 必须在12:00前（Eve参加）
                        if time_to_minutes(starts[4]) >= 12 * 60:
                            # 会议5是Client Demo
                            continue
                        
                        # 检查约束 6: Budget Planning (会议3) 必须在 Tech Design (会议2) 之前
                        if time_to_minutes(starts[2]) >= time_to_minutes(starts[1]):
                            # 会议3是Budget Planning，会议2是Tech Design
                            continue
                        
                        # 检查人员冲突
                        meeting_schedule = []
                        for i, meeting in enumerate(meetings):
                            meeting_schedule.append({
                                "id": meeting["id"],
                                "name": meeting["name"],
                                "start": starts[i],
                                "end": minutes_to_time(time_to_minutes(starts[i]) + 60),
                                "participants": meeting["participants"]
                            })
                        
                        # 检查每个人是否有时间冲突
                        people = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry"]
                        people_conflict = False
                        
                        for person in people:
                            person_meetings = []
                            for meeting in meeting_schedule:
                                if person in meeting["participants"]:
                                    person_meetings.append({
                                        "start": time_to_minutes(meeting["start"]),
                                        "end": time_to_minutes(meeting["end"]),
                                        "name": meeting["name"]
                                    })
                            
                            # 检查此人是否有会议时间重叠
                            for i in range(len(person_meetings)):
                                for j in range(i+1, len(person_meetings)):
                                    m1 = person_meetings[i]
                                    m2 = person_meetings[j]
                                    # 如果有重叠（即使只有1分钟）
                                    if not (m1["end"] <= m2["start"] or m2["end"] <= m1["start"]):
                                        people_conflict = True
                                        break
                                if people_conflict:
                                    break
                            if people_conflict:
                                break
                        
                        if people_conflict:
                            continue
                        
                        # 检查约束 4: Bob 在 11:00-14:00 之间不可用
                        bob_meetings = []
                        for meeting in meeting_schedule:
                            if "Bob" in meeting["participants"]:
                                start_min = time_to_minutes(meeting["start"])
                                end_min = time_to_minutes(meeting["end"])
                                # 检查会议是否与Bob不可用时间有重叠
                                if start_min < 14*60 and end_min > 11*60:
                                    # 会议与11:00-14:00有重叠
                                    bob_meetings.append(meeting["name"])
                        
                        if bob_meetings:
                            # Bob有会议在11:00-14:00之间，检查是否完全在不可用时间外
                            for meeting in meeting_schedule:
                                if "Bob" in meeting["participants"]:
                                    start_min = time_to_minutes(meeting["start"])
                                    end_min = time_to_minutes(meeting["end"])
                                    # 如果会议完全在11:00-14:00之外，允许
                                    if not (end_min <= 11*60 or start_min >= 14*60):
                                        # 会议与不可用时间有重叠
                                        continue
                        
                        # 分配会议室
                        # 按开始时间排序会议
                        sorted_meetings = sorted(meeting_schedule, key=lambda x: time_to_minutes(x["start"]))
                        
                        # 分配房间，确保同一时间不超过2个会议
                        room_assignments = {}
                        for meeting in sorted_meetings:
                            room_assignments[meeting["id"]] = ""
                        
                        # 简单的房间分配：按时间顺序交替分配房间
                        room_index = 0
                        for meeting in sorted_meetings:
                            room_assignments[meeting["id"]] = rooms[room_index % 2]
                            room_index += 1
                        
                        # 构建最终方案
                        solution = []
                        for meeting in meeting_schedule:
                            solution.append({
                                "meeting": meeting["name"],
                                "start_time": meeting["start"],
                                "end_time": meeting["end"],
                                "room": room_assignments[meeting["id"]],
                                "participants": meeting["participants"]
                            })
                        
                        solutions.append(solution)
                        
                        # 找到一个解就返回
                        if solutions:
                            print(f"找到 {len(solutions)} 个解决方案")
                            return solutions[0]
    
    print("未找到解决方案")
    return None

if __name__ == "__main__":
    solution = main()
    if solution:
        print("\n找到的解决方案:")
        for item in solution:
            print(f"{item['meeting']}: {item['start_time']}-{item['end_time']} (Room {item['room']}) - {item['participants']}")
        
        # 保存到JSON文件
        with open("schedule.json", "w") as f:
            json.dump(solution, f, indent=2)
        print("\n已保存到 schedule.json")
    else:
        print("未找到满足所有约束的解决方案")
