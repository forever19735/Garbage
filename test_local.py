#!/usr/bin/env python3
"""
本地測試腳本 - 測試週期計算和資料結構
無需 LINE 或 Firebase 連接
"""

from datetime import date, timedelta

def test_week_calculation():
    """測試自然週計算邏輯"""
    print("=" * 50)
    print("測試：自然週計算")
    print("=" * 50)
    
    # 模擬資料
    base_date = date(2026, 1, 13)  # 週一
    today = date.today()
    
    # 計算基準日期所在自然週的星期一
    base_monday = base_date - timedelta(days=base_date.weekday())
    
    # 計算今天所在自然週的星期一
    today_monday = today - timedelta(days=today.weekday())
    
    # 計算相差多少個自然週
    weeks_diff = (today_monday - base_monday).days // 7
    
    print(f"基準日期: {base_date} ({get_weekday_name(base_date)})")
    print(f"基準星期一: {base_monday}")
    print(f"今天: {today} ({get_weekday_name(today)})")
    print(f"今天星期一: {today_monday}")
    print(f"相差週數: {weeks_diff}")
    
    # 假設有 3 週輪值
    total_weeks = 3
    current_week = (weeks_diff % total_weeks) + 1
    
    print(f"\n總輪值週數: {total_weeks}")
    print(f"當前週次: 第 {current_week} 週")
    print()

def test_member_rotation():
    """測試成員輪值邏輯"""
    print("=" * 50)
    print("測試：成員輪值")
    print("=" * 50)
    
    # 模擬群組資料
    groups = {
        "test_group_1": {
            "1": ["Alice", "Bob"],
            "2": ["Charlie"],
            "3": ["David", "Eve"]
        }
    }
    
    # 模擬排程資料
    schedules = {
        "test_group_1": {
            "days": "mon,wed,fri",
            "hour": 18,
            "minute": 0
        }
    }
    
    group_id = "test_group_1"
    
    print(f"群組 ID: {group_id}")
    print(f"\n週次成員設定:")
    for week, members in groups[group_id].items():
        print(f"  第 {week} 週: {', '.join(members)}")
    
    schedule = schedules[group_id]
    print(f"\n排程設定:")
    print(f"  推播日: {schedule['days']}")
    print(f"  推播時間: {schedule['hour']:02d}:{schedule['minute']:02d}")
    print()

def test_day_member_assignment():
    """測試週內按日分配成員"""
    print("=" * 50)
    print("測試：週內按日分配成員")
    print("=" * 50)
    
    broadcast_days = ["mon", "wed", "fri"]
    current_members = ["Alice", "Bob", "Charlie"]
    
    day_mapping = {
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    print(f"推播日: {', '.join(broadcast_days)}")
    print(f"本週成員: {', '.join(current_members)}")
    print(f"\n分配結果:")
    
    for day_name in broadcast_days:
        day_index = broadcast_days.index(day_name)
        member_index = day_index % len(current_members)
        member = current_members[member_index]
        
        print(f"  {day_name.upper()} ({get_weekday_chinese(day_mapping[day_name])}): {member}")
    print()

def test_validation():
    """測試輸入驗證"""
    print("=" * 50)
    print("測試：輸入驗證")
    print("=" * 50)
    
    # 測試時間驗證
    test_times = ["18:00", "25:00", "abc", "12:60", "09:30"]
    
    print("時間格式驗證:")
    for time_str in test_times:
        result = validate_time(time_str)
        status = "✅" if result["valid"] else "❌"
        print(f"  {status} {time_str}: {result['message']}")
    
    print()
    
    # 測試星期驗證
    test_days = ["mon,wed,fri", "xyz", "mon,xyz,wed", "tue,thu"]
    
    print("星期格式驗證:")
    for days_str in test_days:
        result = validate_days(days_str)
        status = "✅" if result["valid"] else "❌"
        print(f"  {status} {days_str}: {result['message']}")
    
    print()

def validate_time(time_str):
    """驗證時間格式"""
    if ':' not in time_str:
        return {"valid": False, "message": "缺少 ':'"}
    
    parts = time_str.split(':')
    if len(parts) != 2:
        return {"valid": False, "message": "格式錯誤"}
    
    try:
        hour = int(parts[0])
        minute = int(parts[1])
        
        if not (0 <= hour <= 23):
            return {"valid": False, "message": "小時必須在 0-23 之間"}
        if not (0 <= minute <= 59):
            return {"valid": False, "message": "分鐘必須在 0-59 之間"}
        
        return {"valid": True, "message": f"有效時間 {hour:02d}:{minute:02d}"}
    except ValueError:
        return {"valid": False, "message": "必須是數字"}

def validate_days(days_str):
    """驗證星期格式"""
    valid_days = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
    days = [d.strip().lower() for d in days_str.split(',')]
    
    invalid = [d for d in days if d not in valid_days]
    if invalid:
        return {"valid": False, "message": f"無效的星期: {', '.join(invalid)}"}
    
    return {"valid": True, "message": f"有效星期: {', '.join(days)}"}

def get_weekday_name(date_obj):
    """取得星期英文名稱"""
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return weekdays[date_obj.weekday()]

def get_weekday_chinese(weekday_num):
    """取得星期中文名稱"""
    weekdays = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
    return weekdays[weekday_num]

if __name__ == "__main__":
    print("\n🧪 LINE Bot 本地測試腳本")
    print("=" * 50)
    print()
    
    test_week_calculation()
    test_member_rotation()
    test_day_member_assignment()
    test_validation()
    
    print("=" * 50)
    print("✅ 所有本地測試完成！")
    print("\n下一步:")
    print("1. 如需測試完整功能，請先部署到 Zeabur")
    print("2. 運行 /deploy workflow 進行部署")
    print("3. 部署後在 LINE 群組中測試指令")
    print("=" * 50)
