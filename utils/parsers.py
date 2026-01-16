"""Utility functions for parsing user input"""
import re
from typing import Tuple, Optional, List

# 錯誤訊息範本
ERROR_TEMPLATES = {
    'time_format': "❌ 時間格式錯誤\n📍 您輸入的：{input}\n⚠️ 問題：{issue}\n✅ 正確格式：@time 18:30\n💡 範例：@time 09:00 或 @time 17:30",
    'hour_range': "❌ 小時超出範圍\n📍 您輸入的小時：{hour}\n⚠️ 小時必須在 0-23 之間\n✅ 正確範例：@time 18:30",
    'minute_range': "❌ 分鐘超出範圍\n📍 您輸入的分鐘：{minute}\n⚠️ 分鐘必須在 0-59 之間\n✅ 正確範例：@time 18:30",
    'day_format': "❌ 星期格式錯誤\n📍 您輸入的：{input}\n⚠️ 支援的星期：mon, tue, wed, thu, fri, sat, sun\n✅ 正確範例：@day mon,thu 或 @day mon,wed,fri",
    'week_format': "❌ 週數格式錯誤\n📍 您輸入的：{input}\n⚠️ 週數必須是正整數（1, 2, 3...）\n✅ 正確範例：@week 1 Alice,Bob",
    'cron_format': "❌ 排程格式錯誤\n📍 您輸入的：{input}\n⚠️ 正確格式：@cron 星期 時:分\n✅ 正確範例：@cron mon,thu 18:30",
    'unknown_command': "❓ 找不到指令「{command}」\n\n{suggestions}\n💡 輸入 @help 查看所有指令",
}


def parse_time_flexible(time_str: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    """
    彈性解析時間字串，支援多種格式
    
    Args:
        time_str: 時間字串
        
    Returns:
        tuple: (hour, minute, error_message) 或 (None, None, error_message)
    """
    time_str = time_str.strip()
    
    # 支援的格式：HH:MM, HH MM, HHMM
    patterns = [
        r'^(\d{1,2}):(\d{2})$',      # 18:30
        r'^(\d{1,2})\s+(\d{2})$',    # 18 30
        r'^(\d{2})(\d{2})$',         # 1830
    ]
    
    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            try:
                hour = int(match.group(1))
                minute = int(match.group(2))
                
                # 驗證範圍
                if not (0 <= hour <= 23):
                    return None, None, ERROR_TEMPLATES['hour_range'].format(hour=hour)
                if not (0 <= minute <= 59):
                    return None, None, ERROR_TEMPLATES['minute_range'].format(minute=minute)
                
                return hour, minute, None
            except ValueError:
                pass
    
    # 無法解析
    return None, None, ERROR_TEMPLATES['time_format'].format(
        input=time_str,
        issue="無法識別的時間格式"
    )


def parse_members_flexible(members_str: str) -> List[str]:
    """
    彈性解析成員列表，支援多種分隔符
    
    Args:
        members_str: 成員字串
        
    Returns:
        list: 成員列表
    """
    # 支援的分隔符：逗號、空格、頓號、分號
    # 先統一替換為逗號
    members_str = members_str.replace('、', ',')
    members_str = members_str.replace('；', ',')
    members_str = members_str.replace(';', ',')
    
    # 如果沒有逗號，嘗試用空格分隔
    if ',' not in members_str:
        members = members_str.split()
    else:
        members = members_str.split(',')
    
    # 清理並過濾空字串
    members = [m.strip() for m in members if m.strip()]
    
    return members
