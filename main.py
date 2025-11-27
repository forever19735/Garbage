from flask import Flask, request, abort
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging.models import PushMessageRequest, TextMessage
from linebot.v3.webhooks import TextMessageContent, JoinEvent, LeaveEvent
import os
import json
import requests
import firebase_service

# 載入 .env 檔案中的環境變數（僅在本地開發時使用）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 在生產環境中（如 Railway）沒有 python-dotenv，直接忽略
    pass

# ===== 統一資料管理類別 =====
class DataManager:
    """統一的資料管理類別，完全使用 Firebase 存儲"""
    
    def __init__(self):
        self.firebase_service = firebase_service.firebase_service_instance
    
    def load_data(self, data_type, default_value=None):
        """從 Firebase 載入資料"""
        if not self.firebase_service.is_available():
            print(f"⚠️ Firebase 未連接，無法載入 {data_type}")
            return default_value if default_value is not None else ([] if data_type in ['group_ids'] else {})
        
        try:
            if data_type == 'group_ids':
                firebase_data = self.firebase_service.load_group_ids()
            elif data_type == 'groups':
                firebase_data = self.firebase_service.load_groups()
            elif data_type == 'base_date':
                firebase_data = self.firebase_service.load_base_date()
            elif data_type == 'group_schedules':
                firebase_data = self.firebase_service.load_group_schedules()
            else:
                firebase_data = None
            
            if firebase_data is not None:
                return firebase_data
        except Exception as e:
            print(f"⚠️ 從 Firebase 載入 {data_type} 失敗: {e}")
        
        return default_value if default_value is not None else ([] if data_type in ['group_ids'] else {})
    
    def save_data(self, data_type, data):
        """儲存資料到 Firebase"""
        if not self.firebase_service.is_available():
            print(f"⚠️ Firebase 未連接，無法儲存 {data_type}")
            return False
        
        try:
            if data_type == 'group_ids':
                return self.firebase_service.save_group_ids(data)
            elif data_type == 'groups':
                return self.firebase_service.save_groups(data)
            elif data_type == 'base_date':
                return self.firebase_service.save_base_date(data)
            elif data_type == 'group_schedules':
                return self.firebase_service.save_group_schedules(data)
            elif data_type == 'group_messages':
                return self.firebase_service.save_group_messages(data)
        except Exception as e:
            print(f"⚠️ 儲存 {data_type} 到 Firebase 失敗: {e}")
            return False
        
        return False
    
    def delete_data(self, data_type):
        """從 Firebase 刪除資料"""
        if not self.firebase_service.is_available():
            print(f"⚠️ Firebase 未連接，無法刪除 {data_type}")
            return False
        
        try:
            if data_type == 'base_date':
                return self.firebase_service.reset_base_date()
        except Exception as e:
            print(f"⚠️ 從 Firebase 刪除 {data_type} 失敗: {e}")
            return False
        
        return False

# 創建全域資料管理器實例
data_manager = DataManager()

app = Flask(__name__)

# ===== 簡化的資料操作函數 =====
def load_group_ids():
    """載入群組 ID 列表"""
    return data_manager.load_data('group_ids', [])

def save_group_ids():
    """儲存群組 ID 列表"""
    return data_manager.save_data('group_ids', group_ids)

def load_groups():
    """載入成員群組資料"""
    return data_manager.load_data('groups', {})

def save_groups():
    """儲存成員群組資料"""
    result = data_manager.save_data('groups', groups)
    return result

def load_base_date():
    """載入基準日期"""
    return data_manager.load_data('base_date')

def save_base_date(base_date):
    """儲存基準日期"""
    return data_manager.save_data('base_date', base_date)

def reset_base_date():
    """重置基準日期"""
    global base_date
    base_date = None
    return data_manager.delete_data('base_date')

def load_group_schedules():
    """載入群組排程設定"""
    return data_manager.load_data('group_schedules', {})

def save_group_schedules(schedules):
    """儲存群組排程設定"""
    result = data_manager.save_data('group_schedules', schedules)
    return result

def load_group_messages():
    """載入群組自訂文案設定"""
    return data_manager.load_data('group_messages', {})

def save_group_messages():
    """儲存群組自訂文案設定"""
    return data_manager.save_data('group_messages', group_messages)




    return firebase_success
# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 載入持久化的群組 ID 列表
group_ids = load_group_ids()
groups = load_groups()  # 儲存每週的成員名單
base_date = load_base_date()  # 儲存基準日期（第一週開始日期）
group_schedules = load_group_schedules()  # 載入群組排程設定
group_messages = load_group_messages()  # 載入群組自訂文案設定

# 載入數據 - 直接從 Firebase 載入
if firebase_service.firebase_service_instance.is_available():
    print("✅ Firebase 可用，直接從 Firebase 載入資料")

# 載入群組排程設定
group_schedules = load_group_schedules()

# 從環境變數載入已知的群組 ID（補充載入，支援舊版設定）
if os.getenv("LINE_GROUP_ID"):
    # 正確解析環境變數中的群組 ID（支援多個群組，以逗號分隔）
    env_group_ids = [gid.strip() for gid in os.getenv("LINE_GROUP_ID").split(",") if gid.strip()]
    for gid in env_group_ids:
        if gid not in group_ids:
            group_ids.append(gid)
            print(f"✅ 從 LINE_GROUP_ID 補充載入群組: {gid}")


print("ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
print("CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
# 確認 group ids 有沒有設定
print("GROUP_ID:", group_ids)
print("RAW LINE_GROUP_ID:", repr(os.getenv("LINE_GROUP_ID")))
print("所有環境變數:")
for key, value in os.environ.items():
    if 'LINE' in key.upper():
        print(f"  {key}: {repr(value)}")

# 檢查必要的環境變數
if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("警告：LINE Bot 環境變數未設定！")
    print("請設定以下環境變數：")
    print("- LINE_CHANNEL_ACCESS_TOKEN")
    print("- LINE_CHANNEL_SECRET")
    print("- LINE_GROUP_ID (可選，Bot 加入群組會自動記錄)")
    
    # 在本地測試時，如果環境變數未設定，就不初始化 LINE Bot API
    if not LINE_CHANNEL_ACCESS_TOKEN:
        LINE_CHANNEL_ACCESS_TOKEN = "dummy_token_for_testing"
    if not LINE_CHANNEL_SECRET:
        LINE_CHANNEL_SECRET = "dummy_secret_for_testing"

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===== 成員輪值設定 =====
# groups 變數已從持久化檔案載入

# ===== 判斷當週誰要收垃圾 =====
def get_current_group(group_id=None):
    """
    取得當前週的成員群組（基於自然週計算：星期一到星期日）
    
    Args:
        group_id (str): 指定群組ID，如果為None則使用legacy模式
    
    Returns:
        list: 當前週的成員列表
    """
    global base_date
    
    if not isinstance(groups, dict) or len(groups) == 0:
        return []
    
    # 決定使用哪個群組的資料
    if group_id is None:
        # 向後相容模式：使用legacy群組或第一個可用群組
        if "legacy" in groups:
            group_data = groups["legacy"]
        elif groups:
            group_data = next(iter(groups.values()))
        else:
            return []
    else:
        # 指定群組模式
        if group_id not in groups:
            return []
        group_data = groups[group_id]
    
    if not isinstance(group_data, dict) or len(group_data) == 0:
        return []
    
    today = date.today()
    
    # 檢查並修復 base_date 的類型
    if base_date is None or not isinstance(base_date, date):
        print(f"⚠️ base_date 類型錯誤: {type(base_date)}, 值: {base_date}, 重置為今天")
        base_date = today
        save_base_date(base_date)
    
    # 計算基準日期所在自然週的星期一
    base_monday = base_date - timedelta(days=base_date.weekday())
    
    # 計算今天所在自然週的星期一
    today_monday = today - timedelta(days=today.weekday())
    
    # 計算相差多少個自然週
    weeks_diff = (today_monday - base_monday).days // 7
    
    # 計算當前是第幾週（從第1週開始）
    total_weeks = len(group_data)
    if total_weeks == 0:
        return []
    
    current_week = (weeks_diff % total_weeks) + 1
    
    week_key = str(current_week)
    return group_data.get(week_key, [])

def get_current_day_member(group_id, target_date=None):
    """
    取得當前日期對應的輪值成員（支援週內按日輪值）
    
    Args:
        group_id (str): 群組ID
        target_date (date): 目標日期，如果為None則使用今天
    
    Returns:
        str: 當天負責的成員名稱，如果沒有則回傳None
    """
    if target_date is None:
        target_date = date.today()
    
    # 取得該群組的成員列表
    current_members = get_current_group(group_id)
    if not current_members:
        return None
    
    # 取得該群組的排程設定
    if group_id not in group_schedules:
        return current_members[0] if current_members else None
    
    schedule = group_schedules[group_id]
    if 'days' not in schedule:
        return current_members[0] if current_members else None
    
    # 取得推播日列表
    broadcast_days = schedule['days']
    
    # 如果是字串格式，轉換為列表
    if isinstance(broadcast_days, str):
        broadcast_days = [d.strip() for d in broadcast_days.split(',')]
    elif not isinstance(broadcast_days, list):
        return current_members[0] if current_members else None
    
    # 將英文星期轉換為數字 (Monday=0, Sunday=6)
    day_mapping = {
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    # 取得今天是星期幾
    today_weekday = target_date.weekday()
    
    # 檢查今天是否在推播日列表中
    today_day_name = None
    for day_name, day_num in day_mapping.items():
        if day_num == today_weekday:
            today_day_name = day_name
            break
    
    if today_day_name not in broadcast_days:
        return None  # 今天不是推播日
    
    # 找出今天是該週的第幾個推播日
    day_index = broadcast_days.index(today_day_name)
    
    # 根據推播日的順序分配成員
    member_index = day_index % len(current_members)
    return current_members[member_index]

# ===== 輔助函數 =====
def get_group_id_from_event(event):
    """
    從 LINE event 物件中提取群組 ID
    
    Args:
        event: LINE message event 物件
        
    Returns:
        str: 群組 ID，如果不是群組訊息則回傳 None
    """
    try:
        # 嘗試取得群組 ID
        if hasattr(event.source, 'group_id'):
            return event.source.group_id
        else:
            # 如果沒有 group_id 屬性，可能是私訊，回傳 None
            return None
    except Exception as e:
        print(f"取得群組 ID 失敗: {e}")
        return None

# ===== 成員輪值管理函數 =====
def get_member_schedule(group_id=None):
    """
    取得目前的成員輪值安排（基於自然週計算）
    
    Args:
        group_id (str): 指定群組ID，如果為None則使用legacy模式
    
    Returns:
        dict: 包含成員輪值資訊的字典
    """
    global base_date
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        return {
            "total_weeks": 0,
            "current_week": 1,
            "base_date": None,
            "group_id": group_id,
            "schedule": {},
            "current_members": []
        }
    
    # 決定使用哪個群組的資料
    if group_id is None:
        # 向後相容模式：使用legacy群組或第一個可用群組
        if "legacy" in groups:
            group_data = groups["legacy"]
            effective_group_id = "legacy"
        elif groups:
            effective_group_id = next(iter(groups.keys()))
            group_data = groups[effective_group_id]
        else:
            return {
                "total_weeks": 0,
                "current_week": 1,
                "base_date": None,
                "group_id": group_id,
                "schedule": {},
                "current_members": []
            }
    else:
        # 指定群組模式
        if group_id not in groups:
            return {
                "total_weeks": 0,
                "current_week": 1,
                "base_date": None,
                "group_id": group_id,
                "schedule": {},
                "current_members": []
            }
        group_data = groups[group_id]
        effective_group_id = group_id
    
    if not isinstance(group_data, dict):
        return {
            "total_weeks": 0,
            "current_week": 1,
            "base_date": None,
            "group_id": effective_group_id,
            "schedule": {},
            "current_members": []
        }
    
    total_weeks = len(group_data)
    today = date.today()
    
    # 檢查並修復 base_date 的類型，如果沒有基準日期且有成員設定，使用當天作為基準
    if (base_date is None or not isinstance(base_date, date)) and total_weeks > 0:
        if base_date is not None:
            print(f"⚠️ base_date 類型錯誤: {type(base_date)}, 值: {base_date}, 重置為今天")
        base_date = today
        save_base_date(base_date)
    
    # 計算當前週（使用自然週）
    if base_date is not None and total_weeks > 0:
        # 計算基準日期所在自然週的星期一
        base_monday = base_date - timedelta(days=base_date.weekday())
        
        # 計算今天所在自然週的星期一
        today_monday = today - timedelta(days=today.weekday())
        
        # 計算相差多少個自然週
        weeks_diff = (today_monday - base_monday).days // 7
        current_week = (weeks_diff % total_weeks) + 1
        
        # 計算距離基準週開始的總天數
        days_since_start = (today - base_monday).days
    else:
        current_week = 1
        days_since_start = 0
        weeks_diff = 0
    
    # 取得當前週的成員
    current_week_key = str(current_week)
    current_members = group_data.get(current_week_key, [])
    
    schedule_info = {
        "total_weeks": total_weeks,
        "current_week": current_week,
        "base_date": base_date.isoformat() if base_date else None,
        "group_id": effective_group_id,
        "calculation_method": "natural_week",
        "days_since_start": days_since_start,
        "weeks_diff": weeks_diff,
        "current_members": current_members,
        "weeks": []
    }
    
    # 建立週次資訊
    for week_key in sorted(group_data.keys(), key=lambda x: int(x)):
        week_num = int(week_key)
        week_members = group_data[week_key]
        week_info = {
            "week": week_num,
            "members": week_members.copy(),
            "member_count": len(week_members),
            "is_current": week_num == current_week
        }
        schedule_info["weeks"].append(week_info)
    
    return schedule_info

def update_member_schedule(week_num, members, group_id=None):
    """
    更新指定週的成員安排
    
    Args:
        week_num (int): 週數 (1-based)
        members (list): 成員列表
        group_id (str): 群組ID，如果為None則使用legacy模式
        
    Returns:
        dict: 操作結果
    """
    global groups, base_date
    
    if not isinstance(week_num, int) or week_num < 1:
        return {"success": False, "message": "週數必須是大於 0 的整數"}
    
    if not isinstance(members, list) or len(members) == 0:
        return {"success": False, "message": "成員列表不能為空"}
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        groups = {}
    
    # 決定使用哪個群組
    if group_id is None:
        # 向後相容模式：使用legacy群組
        target_group_id = "legacy"
    else:
        target_group_id = group_id
    
    # 確保群組存在
    if target_group_id not in groups:
        groups[target_group_id] = {}
    
    # 更新成員
    week_key = str(week_num)
    groups[target_group_id][week_key] = members.copy()
    
    # 如果這是第一次設定成員且沒有基準日期，設定基準日期
    if base_date is None:
        base_date = date.today()
        save_base_date(base_date)
    
    # 儲存更新
    save_groups()
    
    group_display = f" (群組: {target_group_id})" if target_group_id != "legacy" else ""
    return {
        "success": True,
        "message": f"已設定第 {week_num} 週成員：{', '.join(members)}"
    }
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        groups = {}
    
    # 如果是第一次設定成員，記錄基準日期
    if len(groups) == 0 and base_date is None:
        base_date = date.today()
        save_base_date(base_date)
    
    # 更新指定週的成員
    groups[str(week_num)] = members.copy()
    save_groups()  # 立即儲存到檔案
    
    return {
        "success": True,
        "message": f"第 {week_num} 週成員已更新為: {', '.join(members)}",
        "week": week_num,
        "members": members.copy(),
        "total_weeks": len(groups)
    }

def add_member_to_week(week_num, member_name):
    """
    添加成員到指定週
    
    Args:
        week_num (int): 週數 (1-based)
        member_name (str): 成員名稱
        
    Returns:
        dict: 操作結果
    """
    global groups, base_date
    
    if not isinstance(week_num, int) or week_num < 1:
        return {"success": False, "message": "週數必須是大於 0 的整數"}
    
    if not member_name or not isinstance(member_name, str):
        return {"success": False, "message": "成員名稱不能為空"}
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        groups = {}
    
    # 如果是第一次設定成員，記錄基準日期
    if len(groups) == 0 and base_date is None:
        base_date = date.today()
        save_base_date(base_date)
    
    # 初始化週數鍵值
    week_key = str(week_num)
    if week_key not in groups:
        groups[week_key] = []
    
    # 檢查成員是否已存在
    if member_name in groups[week_key]:
        return {"success": False, "message": f"成員 {member_name} 已在第 {week_num} 週"}
    
    # 添加成員
    groups[week_key].append(member_name)
    save_groups()  # 立即儲存到檔案
    
    return {
        "success": True,
        "message": f"成功添加 {member_name} 到第 {week_num} 週",
        "week": week_num,
        "member": member_name,
        "current_members": groups[week_key].copy()
    }

def remove_member_from_week(week_num, member_name):
    """
    從指定週移除成員
    
    Args:
        week_num (int): 週數 (1-based)
        member_name (str): 成員名稱
        
    Returns:
        dict: 操作結果
    """
    global groups
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        groups = {}
    
    week_key = str(week_num)
    
    if not isinstance(week_num, int) or week_num < 1:
        return {"success": False, "message": "週數必須是大於 0 的整數"}
    
    if week_key not in groups:
        return {"success": False, "message": f"第 {week_num} 週沒有成員安排"}
    
    if not member_name or not isinstance(member_name, str):
        return {"success": False, "message": "成員名稱不能為空"}
    
    # 檢查成員是否存在
    if member_name not in groups[week_key]:
        return {"success": False, "message": f"成員 {member_name} 不在第 {week_num} 週"}
    
    # 移除成員
    groups[week_key].remove(member_name)
    save_groups()  # 立即儲存到檔案
    
    return {
        "success": True,
        "message": f"成員 {member_name} 已從第 {week_num} 週移除",
        "week": week_num,
        "remaining_members": groups[week_key].copy(),
        "total_members": len(groups[week_key])
    }

def get_member_schedule_summary(group_id=None):
    """
    取得成員輪值的簡要摘要，用於顯示給使用者
    
    Args:
        group_id (str): 指定群組ID，如果為None則使用legacy模式
    
    Returns:
        str: 格式化的成員輪值摘要字串
    """
    schedule = get_member_schedule(group_id)
    
    if schedule["total_weeks"] == 0:
        group_info = f" (群組: {group_id})" if group_id and group_id != "legacy" else ""
        return f"👥 尚未設定成員輪值表{group_info}\n\n💡 使用「@week 1 小明,小華」來設定第1週的成員"
    
    group_info = f" (群組: {schedule['group_id']})" if schedule['group_id'] != "legacy" else ""
    summary = f"👥 輪值成員表\n\n"
    summary += f"📅 總共 {schedule['total_weeks']} 週輪值\n"
    summary += f"📍 目前第 {schedule['current_week']} 週\n"
    
    # 顯示基準日期資訊
    if schedule["base_date"]:
        from datetime import datetime
        base_date_obj = datetime.fromisoformat(schedule["base_date"]).date()
        base_monday = base_date_obj - timedelta(days=base_date_obj.weekday())
        
        summary += f"📆 基準日期: {base_date_obj.strftime('%Y-%m-%d')}\n"
        summary += f"📊 基準週一: {base_monday.strftime('%Y-%m-%d')}\n"
        summary += f"🔄 計算方式: 自然週（週一到週日）\n"
        
        if schedule.get("weeks_diff", 0) > 0:
            summary += f"⏳ 已經過: {schedule['weeks_diff']} 個自然週\n"
    
    summary += "\n"
    
    current_week_members = []
    
    for week_info in schedule["weeks"]:
        week_num = week_info["week"]
        members = week_info["members"]
        is_current = week_info["is_current"]
        
        if is_current:
            current_week_members = members
        
        status = "👈 本週" if is_current else "　　　"
        member_list = "、".join(members) if members else "無成員"
        
        summary += f"第 {week_num} 週: {member_list} {status}\n"
    
    if current_week_members:
        summary += f"\n🗑️ 本週負責: {', '.join(current_week_members)}"
    else:
        summary += f"\n🗑️ 本週負責: 無成員"
    
    return summary

# ===== 清空/重置功能 =====
def clear_all_members():
    """
    清空所有成員輪值安排並重置基準日期
    
    Returns:
        dict: 操作結果
    """
    global groups, base_date
    
    old_count = len(groups) if isinstance(groups, dict) else 0
    old_base_date = base_date
    
    groups = {}
    base_date = None
    
    save_groups()  # 立即儲存到檔案
    reset_base_date()  # 重置基準日期
    
    return {
        "success": True,
        "message": f"已清空所有成員輪值安排並重置基準日期 (原有 {old_count} 週資料)",
        "cleared_weeks": old_count,
        "old_base_date": old_base_date.isoformat() if old_base_date else None
    }

def clear_week_members(week_num):
    """
    清空指定週的成員安排
    
    Args:
        week_num (int): 週數 (1-based)
        
    Returns:
        dict: 操作結果
    """
    global groups
    
    if not isinstance(groups, dict):
        groups = {}
    
    if not isinstance(week_num, int) or week_num < 1:
        return {"success": False, "message": "週數必須是大於 0 的整數"}
    
    week_key = str(week_num)
    
    if week_key not in groups:
        return {"success": False, "message": f"第 {week_num} 週沒有成員安排"}
    
    old_members = groups[week_key].copy()
    del groups[week_key]
    save_groups()  # 立即儲存到檔案
    
    return {
        "success": True,
        "message": f"已清空第 {week_num} 週的成員安排 (原有成員: {', '.join(old_members)})",
        "week": week_num,
        "cleared_members": old_members
    }

def clear_all_group_ids():
    """
    清空所有群組 ID
    
    Returns:
        dict: 操作結果
    """
    global group_ids
    
    old_count = len(group_ids)
    old_ids = group_ids.copy()
    group_ids = []
    save_group_ids()  # 立即儲存到檔案
    
    return {
        "success": True,
        "message": f"已清空所有群組 ID (原有 {old_count} 個)",
        "cleared_count": old_count,
        "cleared_ids": old_ids
    }

def reset_all_data():
    """
    重置所有資料 (成員安排 + 群組 ID + 基準日期 + 排程設定)
    
    Returns:
        dict: 操作結果
    """
    global groups, group_ids, base_date, group_schedules
    
    # 記錄原始資料
    old_groups_count = len(groups) if isinstance(groups, dict) else 0
    old_group_ids_count = len(group_ids)
    old_base_date = base_date
    old_schedules_count = len(group_schedules) if isinstance(group_schedules, dict) else 0
    
    # 清空所有資料
    groups = {}
    group_ids = []
    base_date = None
    group_schedules = {}
    
    # 儲存變更
    save_groups()
    save_group_ids()
    reset_base_date()
    save_group_schedules(group_schedules)
    
    return {
        "success": True,
        "message": f"已重置所有資料 (清空 {old_groups_count} 週成員安排 + {old_group_ids_count} 個群組 ID + {old_schedules_count} 個排程設定 + 基準日期)",
        "cleared_groups": old_groups_count,
        "cleared_group_ids": old_group_ids_count,
        "cleared_schedules": old_schedules_count,
        "old_base_date": old_base_date.isoformat() if old_base_date else None
    }

def get_schedule_info():
    """
    取得目前排程設定資訊
    
    Returns:
        dict: 排程資訊
    """
    import pytz
    from datetime import datetime
    
    # 取得排程器資訊
    jobs = []
    if 'scheduler' in globals() and scheduler.running:
        for job in scheduler.get_jobs():
            next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else '無'
            jobs.append({
                "id": job.id,
                "name": job.name or str(job.func),
                "trigger": str(job.trigger),
                "next_run": next_run
            })
    
    return {
        "scheduler_running": 'scheduler' in globals() and scheduler.running,
        "timezone": "Asia/Taipei",
        "current_time": datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S %Z'),
        "jobs": jobs,
        "job_count": len(jobs)
    }

def get_system_status():
    """
    取得系統狀態摘要
    
    Returns:
        str: 格式化的系統狀態字串
    """
    # 取得各種資料狀態
    groups_info = get_member_schedule()
    group_ids_info = get_line_group_ids()
    
    status = "📊 系統狀態摘要\n\n"
    
    # Firebase 狀態
    firebase_available = firebase_service.firebase_service_instance.is_available()
    status += f"🔥 Firebase:\n"
    status += f"  └ 連接狀態: {'✅ 已連接' if firebase_available else '❌ 未連接'}\n"
    
    if firebase_available:
        try:
            firebase_stats = firebase_service.firebase_service_instance.get_statistics()
            status += f"  └ 文件總數: {firebase_stats.get('total_documents', 0)}\n"
            status += f"  └ 集合數量: {len(firebase_stats.get('collections', {}))}\n"
        except Exception as e:
            status += f"  └ 統計錯誤: {str(e)[:30]}...\n"
    else:
        status += f"  └ 儲存模式: 本地檔案\n"
    
    status += "\n"
    
    # 成員輪值狀態
    status += f"👥 成員輪值:\n"
    status += f"  └ 總週數: {groups_info['total_weeks']}\n"
    status += f"  └ 目前週: {groups_info['current_week']}\n"
    status += f"  └ 計算方式: 自然週（週一到週日）\n"
    
    # 基準日期資訊
    if groups_info.get('base_date'):
        from datetime import datetime
        base_date_obj = datetime.fromisoformat(groups_info['base_date']).date()
        base_monday = base_date_obj - timedelta(days=base_date_obj.weekday())
        
        status += f"  └ 基準日期: {base_date_obj.strftime('%Y-%m-%d')}\n"
        status += f"  └ 基準週一: {base_monday.strftime('%Y-%m-%d')}\n"
        
        if groups_info.get('weeks_diff', 0) > 0:
            status += f"  └ 已過週數: {groups_info['weeks_diff']} 週\n"
    else:
        status += f"  └ 基準日期: 未設定\n"
    
    status += "\n"
    
    # 群組 ID 狀態
    status += f"📱 LINE 群組:\n"
    status += f"  └ 群組數量: {group_ids_info['count']}\n"
    if group_ids_info['group_ids']:
        status += f"  └ 群組列表: {', '.join([gid[:8] + '...' for gid in group_ids_info['group_ids']])}\n\n"
    else:
        status += f"  └ 群組列表: 無\n\n"
    
    # 排程狀態
    try:
        schedule_info = get_schedule_info()
        status += f"⏰ 排程設定:\n"
        status += f"  └ 排程器: {'運行中' if schedule_info['scheduler_running'] else '已停止'}\n"
        status += f"  └ 時區: {schedule_info['timezone']}\n"
        status += f"  └ 任務數量: {schedule_info['job_count']}\n"
        
        if schedule_info['jobs']:
            for job in schedule_info['jobs']:
                status += f"  └ {job['name']}: {job['next_run']}\n"
        
        status += f"\n🕐 目前時間: {schedule_info['current_time']}"
    except Exception as e:
        status += f"⏰ 排程設定:\n"
        status += f"  └ 狀態: 載入失敗 ({str(e)})\n"
        
        # 基本時間資訊
        import pytz
        from datetime import datetime
        current_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S %Z')
        status += f"\n🕐 目前時間: {current_time}"
    
    return status

# ===== 幫助功能 =====
def get_help_message(category=None):
    """
    取得幫助訊息
    
    Args:
        category (str): 指定類別 ('schedule', 'members', 'groups')
        
    Returns:
        str: 格式化的幫助訊息
    """
    
    if category == "schedule":
        return """⏰ 排程管理指令

🕐 查看排程：
@schedule - 顯示目前推播排程

⚙️ 設定排程：
@time HH:MM - 設定推播時間
範例：@time 18:30

@day 星期 - 設定推播星期
範例：@day mon,thu

@cron 星期 時 分 - 同時設定星期和時間
範例：@cron tue,fri 20 15

📋 支援的星期格式：
mon, tue, wed, thu, fri, sat, sun

💡 注意事項：
- 所有時間都是台北時間 (Asia/Taipei)
- 設定後會立即顯示下次執行時間
- 可隨時修改排程設定"""

    elif category == "members":
        return """👥 成員管理指令

📋 查看成員：
@members - 顯示完整輪值表

⚙️ 管理成員：
@week 週數 成員1,成員2 - 設定整週成員
範例：@week 1 Alice,Bob,Charlie

@addmember 週數 成員名 - 添加成員到指定週
範例：@addmember 2 David

@removemember 週數 成員名 - 從指定週移除成員
範例：@removemember 1 Alice

�️ 清空功能：
@clear_week 週數 - 清空指定週的成員
範例：@clear_week 1

@clear_members - 清空所有週的成員安排

�💡 提示：
- 週數從 1 開始
- 成員名稱支援中文和表情符號
- 用逗號分隔多個成員，不要加空格"""

    elif category == "groups":
        return """📱 群組管理指令

⚙️ 管理群組：
💡 將 Bot 加入群組會自動記錄群組 ID
💡 在想要接收提醒的群組中輸入此指令

📊 群組資訊說明：
- Bot 加入群組時會自動記錄
- 支援多個群組同時接收提醒
- 群組 ID 以 'C' 開頭"""

    elif category == "test":
        return """🧪 查看和調試指令

📊 查看資訊：
@schedule - 排程資訊
@members - 成員輪值表

🆘 獲取幫助：
@help - 顯示所有指令
@help 類別 - 顯示特定類別指令
類別：schedule, members, groups, message"""

    elif category == "message":
        return """📝 自訂文案設定指令

🔧 設定文案：
@message 自訂文案內容 - 設定專屬提醒訊息
@message - 查看目前文案設定
@message reset - 恢復預設垃圾收集文案

💡 可用佔位符：
• {name} - 負責人姓名
• {date} - 日期 (MM/DD)
• {weekday} - 星期 (週一到週日)

📋 文案範例：
@message 📋 今天 {date} ({weekday}) 輪到 {name} 值日！
@message 🧹 {name}，該打掃辦公室了！({date})
@message ⚡ {weekday} 提醒：{name} 負責設備檢查
@message 🚮 垃圾收集日：{name} 請記得收垃圾 ({date})

🔄 管理文案：
- 每個群組可設定獨立的提醒文案
- 文案會自動儲存到雲端
- 支援表情符號和自訂格式
- 可隨時恢復預設文案

💡 使用建議：
- 根據不同場景自訂文案（值日、清潔、檢查等）
- 使用表情符號讓提醒更生動
- 善用佔位符讓文案更個人化"""

    else:  # 顯示所有指令概覽
        return """🤖 輪值提醒 Bot 指令大全

 常用指令：
@schedule - 查看推播排程
@members - 查看成員輪值表

⚙️ 排程設定：
@time 18:30 - 設定推播時間
@day mon,thu - 設定推播星期  
@cron mon,thu 18 30 - 同時設定星期和時間

👥 成員管理：
@week 1 Alice,Bob - 設定第1週成員
@addmember 1 Charlie - 添加成員到第1週
@removemember 1 Alice - 從第1週移除成員

📝 文案設定：
@message 自訂提醒文案 - 設定專屬提醒訊息
@message reset - 恢復預設文案

📋 詳細查看：
@help schedule - 排程管理指令說明
@help members - 成員管理指令說明  
@help groups - 群組管理指令說明
@help message - 自訂文案設定說明

💡 使用提示：
- 所有時間都是台北時間
- 群組 ID 會自動記住
- 支援多群組推播
- 成員輪值基於自然週（週一到週日）計算
- 所有設定都會持久化儲存
- 第一次設定成員時會自動記錄基準日期
- 週數按自然週循環，每個星期一自動切換

🏃‍♂️ 新手快速開始：
1. 將 Bot 加入群組 (自動記錄群組)
2. 輸入 @cron mon,thu 18:00 (設定提醒星期和時間)
3. 輸入 @week 1 姓名1,姓名2 (設定第幾週成員)
4. 輸入 @message 今天輪到{name}值日！ (選用：自訂文案)

❓ 需要詳細說明請輸入：@help 類別名稱"""

def get_command_examples():
    """
    取得指令範例
    
    Returns:
        str: 格式化的指令範例
    """
    return """📚 指令範例集

🏃‍♂️ 快速開始：
1. 將 Bot 加入群組 - 自動記錄群組 ID
2. @time 18:00 - 設定晚上6點推播
3. @week 1 Alice,Bob - 設定第1週成員

⏰ 排程設定範例：
@time 07:30 - 早上7:30提醒
@time 18:00 - 晚上6:00提醒
@day mon,wed,fri - 週一三五提醒
@cron sat,sun 09 00 - 週末早上9:00

👥 成員管理範例：
@week 1 小明,小華 - 第1週：小明、小華
@week 2 小美,小強 - 第2週：小美、小強
@addmember 1 小李 - 第1週加入小李
@removemember 2 小強 - 第2週移除小強

📱 多群組設定：
將 Bot 加入群組A - 自動記錄
將 Bot 加入群組B - 自動記錄
兩個群組都會收到提醒

📝 自訂文案範例：
@message 📋 今天 {date} ({weekday}) 輪到 {name} 值日！
@message � {name}，該打掃辦公室了！({date})
@message ⚡ {weekday} 提醒：{name} 負責設備檢查

�🧪 驗證流程：
@members - 查看輪值安排
@schedule - 確認推播時間  

💡 實用技巧：
- 用表情符號標記成員：@week 1 Alice🌟,Bob🔥
- 設定備用成員：@week 3 主要成員,備用成員
- 查看下次提醒：@schedule
- 自訂提醒文案：@message 您的專屬文案"""

# ===== 取得目前設定的群組 ID =====
def get_line_group_ids():
    """
    取得目前設定的 LINE 群組 ID 列表
    
    Returns:
        list: 包含所有已設定群組 ID 的列表
        dict: 包含群組 ID 資訊的詳細字典
    """
    return {
        "group_ids": group_ids.copy(),  # 返回副本避免外部修改
        "count": len(group_ids),
        "is_configured": len(group_ids) > 0,
        "valid_ids": [gid for gid in group_ids if gid and gid.startswith("C") and len(gid) > 10]
    }

def add_line_group_id(group_id):
    """
    添加新的群組 ID 到列表中
    
    Args:
        group_id (str): 要添加的群組 ID
        
    Returns:
        dict: 操作結果
    """
    global group_ids
    
    # 驗證群組 ID 格式
    if not group_id or not isinstance(group_id, str):
        return {"success": False, "message": "群組 ID 不能為空"}
    
    if not group_id.startswith("C") or len(group_id) <= 10:
        return {"success": False, "message": "群組 ID 格式無效，應該以 'C' 開頭且長度大於 10"}
    
    # 檢查是否已存在
    if group_id in group_ids:
        return {"success": False, "message": f"群組 ID {group_id} 已存在"}
    
    # 添加到列表
    group_ids.append(group_id)
    save_group_ids()  # 立即儲存到檔案
    return {
        "success": True, 
        "message": f"成功添加群組 ID: {group_id}",
        "total_groups": len(group_ids)
    }

def remove_line_group_id(group_id):
    """
    從列表中移除指定的群組 ID
    
    Args:
        group_id (str): 要移除的群組 ID
        
    Returns:
        dict: 操作結果
    """
    global group_ids
    
    if group_id in group_ids:
        group_ids.remove(group_id)
        save_group_ids()  # 立即儲存到檔案
        return {
            "success": True,
            "message": f"成功移除群組 ID: {group_id}",
            "total_groups": len(group_ids)
        }
    else:
        return {"success": False, "message": f"群組 ID {group_id} 不存在"}

# ===== 推播時間管理函數 =====
def get_schedule_info(group_id=None):
    """
    取得目前設定的推播排程資訊
    
    Args:
        group_id (str): 群組ID，如果為 None 則回傳所有群組的排程資訊
        
    Returns:
        dict: 包含排程資訊的字典
    """
    global group_jobs, group_schedules
    
    if group_id:
        # 取得特定群組的排程資訊
        job = group_jobs.get(group_id)
        if not job:
            return {
                "is_configured": False,
                "message": f"群組 {group_id} 排程未設定",
                "next_run_time": None,
                "schedule_details": None,
                "group_id": group_id
            }
        
        try:
            # 下次執行時間
            next_run = job.next_run_time
            next_run_str = next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else "未知"
            
            # 從儲存的設定取得資訊
            schedule_config = group_schedules.get(group_id, {})
            
            schedule_details = {
                "timezone": "Asia/Taipei",
                "days": schedule_config.get("days", "mon,thu"),
                "hour": schedule_config.get("hour", 17),
                "minute": schedule_config.get("minute", 10),
                "group_id": group_id
            }
            
            return {
                "is_configured": True,
                "message": f"群組 {group_id} 排程已設定",
                "next_run_time": next_run_str,
                "schedule_details": schedule_details,
                "group_id": group_id
            }
            
        except Exception as e:
            return {
                "is_configured": False,
                "message": f"取得群組 {group_id} 排程資訊失敗: {str(e)}",
                "next_run_time": None,
                "schedule_details": None,
                "error": str(e),
                "group_id": group_id
            }
    else:
        # 回傳所有群組的排程資訊
        all_schedules = {}
        for gid in group_schedules:
            all_schedules[gid] = get_schedule_info(gid)
        
        return {
            "is_configured": len(all_schedules) > 0,
            "message": f"目前有 {len(all_schedules)} 個群組設定排程",
            "all_groups": all_schedules
        }

def update_schedule(group_id, days=None, hour=None, minute=None):
    """
    更新群組推播排程設定
    
    Args:
        group_id (str): 群組ID
        days (str): 星期設定，例如 "mon,thu"
        hour (int): 小時 (0-23)
        minute (int): 分鐘 (0-59)
        
    Returns:
        dict: 操作結果
    """
    global group_jobs, group_schedules
    
    try:
        # 取得目前設定
        current_info = get_schedule_info(group_id)
        
        # 使用提供的參數或保持目前設定
        if days is None and current_info["is_configured"]:
            days = current_info["schedule_details"]["days"]
        elif days is None:
            days = "mon,thu"  # 預設值
            
        if hour is None and current_info["is_configured"]:
            hour = current_info["schedule_details"]["hour"]
        elif hour is None:
            hour = 17  # 預設值
            
        if minute is None and current_info["is_configured"]:
            minute = current_info["schedule_details"]["minute"]
        elif minute is None:
            minute = 10  # 預設值
        
        # 驗證參數
        if not isinstance(hour, int) or not (0 <= hour <= 23):
            return {"success": False, "message": "小時必須是 0-23 的整數"}
        
        if not isinstance(minute, int) or not (0 <= minute <= 59):
            return {"success": False, "message": "分鐘必須是 0-59 的整數"}
        
        # 驗證星期格式
        valid_days = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
        day_list = [d.strip() for d in days.split(',')]
        if not all(day in valid_days for day in day_list):
            return {"success": False, "message": "星期格式無效，請使用 mon,tue,wed,thu,fri,sat,sun"}
        
        # 移除舊排程
        if group_id in group_jobs:
            group_jobs[group_id].remove()
            del group_jobs[group_id]
        
        # 建立新排程，明確指定時區
        from apscheduler.triggers.cron import CronTrigger
        job = scheduler.add_job(
            lambda: send_group_reminder(group_id), 
            CronTrigger(
                day_of_week=days, 
                hour=hour, 
                minute=minute,
                timezone=pytz.timezone('Asia/Taipei')  # 明確指定時區
            )
        )
        
        # 儲存排程任務和設定
        group_jobs[group_id] = job
        group_schedules[group_id] = {
            "days": days,
            "hour": hour,
            "minute": minute
        }
        
        # 儲存到檔案
        save_group_schedules(group_schedules)
        
        return {
            "success": True,
            "message": f"群組 {group_id} 推播時間已更新為 {days} {hour:02d}:{minute:02d}",
            "schedule": {
                "days": days,
                "time": f"{hour:02d}:{minute:02d}",
                "next_run": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else "未知",
                "group_id": group_id
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"更新群組 {group_id} 排程失敗: {str(e)}", "error": str(e)}

def send_group_reminder(group_id):
    """
    發送特定群組的垃圾收集提醒（支援週內按日輪值）
    
    Args:
        group_id (str): 群組ID
    """
    try:
        # 取得當前日期資訊
        today = datetime.now(pytz.timezone('Asia/Taipei')).date()
        
        # 取得今天負責的成員（週內按日輪值）
        responsible_member = get_current_day_member(group_id, today)
        
        if not responsible_member:
            print(f"群組 {group_id} 今天沒有設定負責成員")
            return
        
        # 格式化日期和星期
        weekday_names = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
        weekday = weekday_names[today.weekday()]
        date_str = f"{today.month}/{today.day}"
        
        # 建立提醒訊息（顯示當天負責的單一成員）
        # 檢查是否有自訂文案
        custom_message = group_messages.get(group_id, "")
        if custom_message:
            # 使用自訂文案，支援 {name}, {date}, {weekday} 佔位符
            message = custom_message.format(
                name=responsible_member,
                date=date_str,
                weekday=weekday
            )
        else:
            # 使用預設的垃圾收集文案
            message = f"🗑️ 今天 {date_str} ({weekday}) 輪到 {responsible_member} 收垃圾！"
        
        print(f"群組 {group_id} 推播訊息: {message}")
        
        # 發送推播到該群組
        if LINE_CHANNEL_ACCESS_TOKEN:
            url = 'https://api.line.me/v2/bot/message/push'
            headers = {
                'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'to': group_id,
                'messages': [{'type': 'text', 'text': message}]
            }
            
            print(f"建立推播請求: to={group_id}, message_length={len(message)}")
            
            response = requests.post(url, headers=headers, json=data)
            print(f"推播成功 - Response: {response}")
        else:
            print("LINE_CHANNEL_ACCESS_TOKEN 未設定，僅印出訊息")
            
    except Exception as e:
        print(f"群組 {group_id} 推播失敗: {e}")

def get_schedule_summary(group_id=None):
    """
    取得排程的簡要摘要，用於顯示給使用者
    
    Args:
        group_id (str): 群組ID，如果為 None 則顯示所有群組的排程
        
    Returns:
        str: 格式化的排程摘要字串
    """
    if group_id:
        # 顯示特定群組的排程
        info = get_schedule_info(group_id)
        
        if not info["is_configured"]:
            return f"❌ 群組 {group_id} 排程未設定"
        
        details = info["schedule_details"]
        if not details:
            return f"❌ 無法取得群組 {group_id} 排程詳情"
        
        # 格式化星期顯示
        days = details.get("days", "未知")
        day_mapping = {
            "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
            "fri": "週五", "sat": "週六", "sun": "週日"
        }
        
        if "," in days:
            day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
            days_chinese = "、".join(day_list)
        else:
            days_chinese = day_mapping.get(days.strip(), days.strip())
        
        # 格式化時間顯示
        hour = details.get("hour", 0)
        minute = details.get("minute", 0)
        time_str = f"{hour:02d}:{minute:02d}"
        
        # 下次執行時間
        next_run = info.get("next_run_time", "未知")
        
        summary = f"""📅 群組垃圾輪值排程

🕐 執行時間: {time_str} (Asia/Taipei)
📆 執行星期: {days_chinese}
⏰ 下次執行: {next_run}

✅ 排程狀態: 已啟動"""
        
        return summary
    else:
        # 顯示所有群組的排程摘要
        if not group_schedules:
            return "❌ 尚未設定任何群組排程"
        
        summary = "📅 所有群組垃圾輪值排程\n\n"
        for gid in group_schedules:
            group_summary = get_schedule_summary(gid)
            summary += group_summary + "\n" + "="*40 + "\n"
        
        return summary.rstrip("\n=")

def send_trash_reminder():
    today = date.today()
    weekday = today.weekday()  # 0=週一, 1=週二, ..., 6=週日
    weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
    print(f"今天是 {today.strftime('%m/%d')}, {weekday_names[weekday]} (weekday={weekday})")
    
    print(f"群組 IDs: {group_ids}")

    if not group_ids:
        print("沒有設定任何群組 ID，無法推播")
        print("請將 Bot 加入群組，Bot 會自動記錄群組 ID")
        return

    # 為每個群組分別處理
    for gid in group_ids:
        print(f"正在處理群組 ID: {gid}")
        
        if not gid:
            print(f"跳過空的群組 ID")
            continue
            
        if not isinstance(gid, str):
            print(f"跳過非字串群組 ID: {type(gid)}")
            continue
            
        if not gid.startswith("C"):
            print(f"跳過無效格式群組 ID: {gid}")
            continue
            
        if len(gid) <= 10:
            print(f"跳過過短的群組 ID: {gid}")
            continue
        
        # 取得該群組的成員輪值
        group = get_current_group(gid)
        print(f"群組 {gid} 當前成員: {group}")
        
        if not group:
            # 檢查是否有自訂文案
            custom_message = group_messages.get(gid, "")
            if custom_message:
                message = f"⚠️ 今天 {today.strftime('%m/%d')} ({weekday_names[weekday]}) 是提醒日！\n💡 請設定成員輪值表\n\n使用指令：@week 1 成員1,成員2"
            else:
                message = f"🗑️ 今天 {today.strftime('%m/%d')} ({weekday_names[weekday]}) 是收垃圾日！\n💡 請設定成員輪值表\n\n使用指令：@week 1 成員1,成員2"
            person = "未設定成員"
        else:
            # 根據星期決定誰收垃圾（可自訂規則）
            # 週一=0, 週二=1, 週三=2, 週四=3, 週五=4, 週六=5, 週日=6
            if weekday in [0, 3]:  # 週一、週四 -> 第一個人
                person = group[0] if len(group) > 0 else "無成員"
            elif weekday in [1, 4]:  # 週二、週五 -> 第二個人  
                person = group[1] if len(group) > 1 else group[0] if len(group) > 0 else "無成員"
            else:  # 其他天數可自訂規則
                person = group[weekday % len(group)] if group else "無成員"
            
            # 檢查是否有自訂文案
            custom_message = group_messages.get(gid, "")
            if custom_message:
                # 使用自訂文案，支援 {name}, {date}, {weekday} 佔位符
                message = custom_message.format(
                    name=person,
                    date=today.strftime('%m/%d'),
                    weekday=weekday_names[weekday]
                )
            else:
                # 使用預設的垃圾收集文案
                message = f"🗑️ 今天 {today.strftime('%m/%d')} ({weekday_names[weekday]}) 輪到 {person} 收垃圾！"
        
        print(f"群組 {gid} 推播訊息: {message}")
        
        # 發送推播到該群組
        try:
            # 檢查 messaging_api 是否已初始化
            if not messaging_api:
                print("MessagingApi 未初始化，請檢查 LINE_CHANNEL_ACCESS_TOKEN")
                continue
                
            req = PushMessageRequest(
                to=gid,
                messages=[TextMessage(text=message)]
            )
            print(f"建立推播請求: to={gid}, message_length={len(message)}")
            
            response = messaging_api.push_message(req)
            print(f"推播成功 - Response: {response}")
        except Exception as e:
            print(f"推播失敗 - {type(e).__name__}: {e}")
            # 特別處理 LINE API 錯誤
            if "invalid" in str(e).lower() and "to" in str(e).lower():
                print(f"群組 ID '{gid}' 可能無效或 Bot 未加入該群組")
                print(f"請確認:")
                print(f"1. Bot 已加入群組 {gid}")
                print(f"2. 群組 ID 正確 (Bot 加入群組會自動記錄)")
            import traceback
            print(f"完整錯誤: {traceback.format_exc()}")
    
    print("所有群組推播處理完成")

# ===== 啟動排程（每週一、四下午 5:10）=====
from apscheduler.triggers.cron import CronTrigger
import pytz
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
group_jobs = {}  # 儲存每個群組的推播任務

def initialize_group_schedules():
    """初始化群組排程設定"""
    global group_schedules, group_jobs
    
    # 為所有現有群組設定預設排程（如果尚未設定）
    for group_id in group_ids:
        if group_id not in group_schedules:
            # 設定預設排程：週一、週四 17:10
            print(f"為群組 {group_id} 設定預設排程")
            result = update_schedule(group_id, "mon,thu", 17, 10)
            if result["success"]:
                print(f"群組 {group_id} 預設排程設定成功")
            else:
                print(f"群組 {group_id} 預設排程設定失敗: {result['message']}")
    
    # 為已存在於 group_schedules 的群組重新建立排程任務
    for group_id, config in group_schedules.items():
        if group_id not in group_jobs:
            print(f"重新建立群組 {group_id} 的排程任務")
            result = update_schedule(
                group_id, 
                config.get("days", "mon,thu"),
                config.get("hour", 17), 
                config.get("minute", 10)
            )
            if result["success"]:
                print(f"群組 {group_id} 排程任務重建成功")
            else:
                print(f"群組 {group_id} 排程任務重建失敗: {result['message']}")

# 初始化排程
initialize_group_schedules()

scheduler.start()

print(f"排程已啟動，目前有 {len(group_jobs)} 個群組排程")
from datetime import datetime
print(f"當前時間: {datetime.now(pytz.timezone('Asia/Taipei'))}")


@app.route("/")
def index():
    return "LINE Trash Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print("收到 LINE Webhook 請求：", body)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)
    return "OK"

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     text = event.message.text.strip()

#         gid = getattr(event.source, "group_id", None)
#         if gid:
#             line_bot_api.push_message(
#                 gid,
#                 TextSendMessage(text=f"群組ID是：{gid}")
#             )
#         else:
#             # 個人聊天室，直接 reply
#             line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text="這不是群組對話，無法取得群組 ID。")
#             )


# ===== 處理訊息事件 =====
@handler.add(MessageEvent)
def handle_message(event):
    # 使用者設定推播星期、時、分指令
    if event.message.text.strip().startswith("@cron"):
        import re
        m = re.match(r"@cron ([a-z,]+) (\d{1,2})[: ](\d{1,2})", event.message.text.strip())
        if m:
            days = m.group(1)
            hour = int(m.group(2))
            minute = int(m.group(3))
            
            # 驗證時間範圍
            if not (0 <= hour <= 23):
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="小時必須在 0-23 之間")]
                )
                messaging_api.reply_message(req)
                return
                
            if not (0 <= minute <= 59):
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="分鐘必須在 0-59 之間")]
                )
                messaging_api.reply_message(req)
                return
            
            group_id = get_group_id_from_event(event)
            
            if group_id:
                # 更新該群組的排程設定
                result = update_schedule(group_id, days, hour, minute)
                
                if result["success"]:
                    message = f"✅ 群組推播時間已更新為 {days} {hour:02d}:{minute:02d} (台北時間)\n⏰ {result['schedule']['next_run']}"
                else:
                    message = f"❌ 設定失敗: {result['message']}"
            else:
                message = "❌ 無法取得群組資訊"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=message)]
            )
            messaging_api.reply_message(req)
        else:
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="格式錯誤，請輸入 @cron mon,thu 18 30 或 @cron mon,thu 18:30")]
            )
            messaging_api.reply_message(req)

    # 使用者設定推播星期指令
    if event.message.text.strip().startswith("@day"):
        import re
        m = re.match(r"@day ([a-z,]+)", event.message.text.strip())
        if m:
            days = m.group(1)
            group_id = get_group_id_from_event(event)
            
            if group_id:
                # 更新該群組的排程設定
                result = update_schedule(group_id, days=days)
                
                if result["success"]:
                    message = f"✅ 群組推播星期已更新為 {days}\n⏰ {result['schedule']['next_run']}"
                else:
                    message = f"❌ 設定失敗: {result['message']}"
            else:
                message = "❌ 無法取得群組資訊"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=message)]
            )
            messaging_api.reply_message(req)
        else:
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="格式錯誤，請輸入 @day mon,thu")]
            )
            messaging_api.reply_message(req)

    if getattr(event.message, "type", None) == "text":
        print("收到訊息:", event.message.text)
        print("來源:", event.source)

        # 使用者設定推播時間指令
        if event.message.text.strip().startswith("@time"):
            import re
            m = re.match(r"@time (\d{1,2}):(\d{2})", event.message.text.strip())
            if m:
                hour = int(m.group(1))
                minute = int(m.group(2))
                
                # 驗證時間範圍
                if not (0 <= hour <= 23):
                    from linebot.v3.messaging.models import ReplyMessageRequest
                    req = ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="小時必須在 0-23 之間")]
                    )
                    messaging_api.reply_message(req)
                    return
                    
                if not (0 <= minute <= 59):
                    from linebot.v3.messaging.models import ReplyMessageRequest
                    req = ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="分鐘必須在 0-59 之間")]
                    )
                    messaging_api.reply_message(req)
                    return
                
                group_id = get_group_id_from_event(event)
                
                if group_id:
                    # 更新該群組的排程設定
                    result = update_schedule(group_id, hour=hour, minute=minute)
                    
                    if result["success"]:
                        message = f"✅ 群組推播時間已更新為 {hour:02d}:{minute:02d} (台北時間)\n⏰ {result['schedule']['next_run']}"
                    else:
                        message = f"❌ 設定失敗: {result['message']}"
                else:
                    message = "❌ 無法取得群組資訊"
                
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=message)]
                )
                messaging_api.reply_message(req)
            else:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式錯誤，請輸入 @time HH:MM")]
                )
                messaging_api.reply_message(req)

        # # 顯示目前已設定的群組列表
        # if event.message.text.strip() == "@groups":
        #     if group_ids:
        #         group_list = "\n".join([f"{i+1}. {gid}" for i, gid in enumerate(group_ids)])
        #         response_text = f"📋 目前已設定的群組 ({len(group_ids)} 個):\n{group_list}"
        #     else:
        #         response_text = "❌ 尚未設定任何群組 ID\n請將 Bot 加入群組，系統會自動記錄群組 ID"
        #     
        #     from linebot.v3.messaging.models import ReplyMessageRequest
        #     req = ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text=response_text)]
        #     )
        #     messaging_api.reply_message(req)
        
        # # 顯示詳細的群組 ID 資訊
        # if event.message.text.strip() == "@info":
        #     group_info = get_line_group_ids()
        #     
        #     if group_info["is_configured"]:
        #         valid_count = len(group_info["valid_ids"])
        #         invalid_count = group_info["count"] - valid_count
        #         
        #         response_text = f"📊 群組 ID 詳細資訊：\n\n"
        #         response_text += f"總群組數：{group_info['count']}\n"
        #         response_text += f"有效群組：{valid_count}\n"
        #         if invalid_count > 0:
        #             response_text += f"無效群組：{invalid_count}\n"
        #         
        #         response_text += f"\n📋 群組列表：\n"
        #         for i, gid in enumerate(group_info["group_ids"], 1):
        #             status = "✅" if gid in group_info["valid_ids"] else "❌"
        #             response_text += f"{i}. {status} {gid}\n"
        #     else:
        #         response_text = "❌ 尚未設定任何群組 ID\n請將 Bot 加入群組，系統會自動記錄群組 ID"
        #     
        #     from linebot.v3.messaging.models import ReplyMessageRequest
        #     req = ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text=response_text)]
        #     )
        #     messaging_api.reply_message(req)
        
        # 顯示推播排程資訊
        if event.message.text.strip() == "@schedule":
            group_id = get_group_id_from_event(event)
            
            if group_id:
                schedule_summary = get_schedule_summary(group_id)
                response_text = schedule_summary
            else:
                response_text = "❌ 無法取得群組資訊"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 顯示成員輪值表
        if event.message.text.strip() == "@members":
            # 取得當前群組ID
            group_id = getattr(event.source, 'group_id', None)
            summary = get_member_schedule_summary(group_id)
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=summary)]
            )
            messaging_api.reply_message(req)
        
        # 系統狀態查詢
        if event.message.text.strip() == "@status":
            status = get_system_status()
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=status)]
            )
            messaging_api.reply_message(req)
        
        # 清空所有成員安排
        if event.message.text.strip() == "@clear_members":
            result = clear_all_members()
            response_text = f"✅ {result['message']}" if result['success'] else f"❌ {result['message']}"
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 清空指定週成員 - 格式: @clear_week 1
        if event.message.text.strip().startswith("@clear_week"):
            import re
            m = re.match(r"@clear_week (\d+)", event.message.text.strip())
            if m:
                week_num = int(m.group(1))
                result = clear_week_members(week_num)
                response_text = f"✅ {result['message']}" if result['success'] else f"❌ {result['message']}"
            else:
                response_text = "❌ 格式錯誤，請輸入 @clear_week 1 (清空第1週)"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 清空所有群組 ID
        if event.message.text.strip() == "@clear_groups":
            result = clear_all_group_ids()
            response_text = f"✅ {result['message']}" if result['success'] else f"❌ {result['message']}"
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 重置所有資料
        if event.message.text.strip() == "@reset_all":
            result = reset_all_data()
            response_text = f"🔄 {result['message']}"
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # Firebase 備份狀態查詢
        if event.message.text.strip() == "@backup":
            try:
                # 檢查 Firebase 連接狀態
                firebase_available = firebase_service.firebase_service_instance.is_available()
                
                if firebase_available:
                    # 創建 Firebase 備份
                    backup_result = firebase_service.firebase_service_instance.create_backup()
                    
                    if backup_result:
                        response_text = """✅ 資料備份已完成！

☁️ 備份位置: Firebase Firestore
🔒 資料安全: 雲端自動保護
📊 備份內容: 群組設定、成員資料、排程設定

� 備份優勢:
• 自動版本控制
• 即時同步
• 無需手動設定
• 企業級可靠性

⚡ 使用 @backup 指令隨時備份資料"""
                    else:
                        response_text = "⚠️ Firebase 備份建立失敗，請稍後再試"
                else:
                    response_text = "❌ Firebase 無法連接，備份功能暫時不可用"
                
            except Exception as e:
                response_text = f"❌ 備份失敗: {str(e)}"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 環境變數詳細診斷指令
        if event.message.text.strip() == "@debug_env":
            import sys
            from datetime import datetime
            
            # 檢查是否在 Railway 環境中
            railway_env_indicators = [
                ("RAILWAY_ENVIRONMENT_NAME", "環境名稱"),
                ("RAILWAY_PROJECT_NAME", "專案名稱"), 
                ("RAILWAY_SERVICE_NAME", "服務名稱"),
                ("RAILWAY_DEPLOYMENT_ID", "部署ID")
            ]
            
            env_status = []
            for var, desc in railway_env_indicators:
                value = os.getenv(var)
                if value:
                    env_status.append(f"✅ {desc}: {value}")
                else:
                    env_status.append(f"❌ {desc}: 未設定")
            
            is_railway = any(os.getenv(var) for var, _ in railway_env_indicators)
            
            # 檢查目標環境變數
            target_vars = [
                ("LINE_CHANNEL_ACCESS_TOKEN", "LINE Access Token"),
                ("LINE_CHANNEL_SECRET", "LINE Channel Secret"),
                ("GARBAGE_BOT_PERSISTENT_DATA", "持久化資料")
            ]
            
            var_status = []
            for var, desc in target_vars:
                value = os.getenv(var)
                if value:
                    length = len(value)
                    masked = value[:8] + "..." if length > 8 else value
                    var_status.append(f"✅ {desc}: {masked} ({length}字符)")
                else:
                    var_status.append(f"❌ {desc}: 未設定")
            
            response_text = f"""🔍 環境變數詳細診斷報告

🚂 Railway 環境檢查：
{'✅ 確認在 Railway 環境中' if is_railway else '⚠️ 不在 Railway 環境中'}

{chr(10).join(env_status)}

🎯 關鍵環境變數狀態：
{chr(10).join(var_status)}

💡 解決建議：
{'🔄 請在 Railway Dashboard 檢查環境變數設定' + chr(10) + '🚀 設定後請重新部署服務讓變數生效' if is_railway else ''}
{'📱 目前在本地環境，無法讀取 Railway 環境變數' if not is_railway else ''}

⚙️ 系統資訊：
• Python: {sys.version.split()[0]}
• 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # Firebase 狀態檢查
        if event.message.text.strip() == "@firebase":
            firebase_available = firebase_service.firebase_service_instance.is_available()
            
            if firebase_available:
                try:
                    firebase_stats = firebase_service.firebase_service_instance.get_statistics()
                    
                    response_text = f"""🔥 Firebase 狀態報告

✅ 連接狀態: 已連接
📊 資料統計:
  └ 總文件數: {firebase_stats.get('total_documents', 0)}
  └ 集合數量: {len(firebase_stats.get('collections', {}))}

📁 集合詳情:"""
                    
                    for collection_name, doc_count in firebase_stats.get('collections', {}).items():
                        response_text += f"\n  └ {collection_name}: {doc_count} 個文件"
                    
                    response_text += f"""

🔄 資料同步: 自動同步到 Firebase
💾 本地備份: 同時保存到本地檔案
⚡ 提示: 所有資料變更都會即時同步"""
                    
                except Exception as e:
                    response_text = f"""🔥 Firebase 狀態報告

✅ 連接狀態: 已連接
❌ 統計錯誤: {str(e)}

💡 建議: Firebase 已連接但取得統計時發生錯誤"""
            else:
                response_text = f"""🔥 Firebase 狀態報告

❌ 連接狀態: 未連接
📝 原因: Firebase 配置未設定或初始化失敗

🔧 設定方式:
1. 設定環境變數 FIREBASE_CONFIG_JSON
2. 或放置 firebase-service-account.json 檔案
3. 或使用 Google Cloud 預設憑證

💾 目前模式: 本地檔案儲存
⚠️ 提醒: 本地檔案可能在部署時遺失"""
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 設定指定週的成員 - 格式: @week 1 成員1,成員2
        if event.message.text.strip().startswith("@week"):
            import re
            m = re.match(r"@week (\d+) (.+)", event.message.text.strip())
            if m:
                week_num = int(m.group(1))
                members_str = m.group(2)
                members = [member.strip() for member in members_str.split(",") if member.strip()]
                
                # 取得當前群組ID
                group_id = getattr(event.source, 'group_id', None)
                
                result = update_member_schedule(week_num, members, group_id)
                
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"{'✅' if result['success'] else '❌'} {result['message']}")]
                )
                messaging_api.reply_message(req)
            else:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式錯誤，請輸入 @week 週數 成員1,成員2\n例如: @week 1 Alice,Bob")]
                )
                messaging_api.reply_message(req)
        
        # 設定自訂文案 - 格式: @message 自訂提醒文案
        if event.message.text.strip().startswith("@message"):
            message_text = event.message.text.strip()
            
            if len(message_text) > 8:  # "@message " 長度為 9
                custom_message = message_text[9:]  # 取得 "@message " 之後的內容
                
                # 取得當前群組ID
                group_id = getattr(event.source, 'group_id', None)
                
                if group_id:
                    global group_messages
                    
                    # 檢查是否要重置為預設
                    if custom_message.strip().lower() == "reset":
                        if group_id in group_messages:
                            del group_messages[group_id]
                            save_group_messages()
                            response_text = "✅ 已恢復為預設的垃圾收集文案！\n\n🗑️ 預設格式：\n今天 {date} ({weekday}) 輪到 {name} 收垃圾！"
                        else:
                            response_text = "💡 目前就是使用預設文案"
                    else:
                        group_messages[group_id] = custom_message
                        save_group_messages()
                        
                        response_text = f"✅ 自訂文案設定成功！\n\n📝 文案內容：\n{custom_message}\n\n💡 可用佔位符：\n• {{name}} - 負責人姓名\n• {{date}} - 日期 (MM/DD)\n• {{weekday}} - 星期\n\n範例：\n📋 今天 {{date}} ({{weekday}}) 輪到 {{name}} 值日！"
                else:
                    response_text = "❌ 只能在群組中設定自訂文案"
            else:
                # 如果只輸入 @message 沒有內容，則顯示目前設定和說明
                group_id = getattr(event.source, 'group_id', None)
                if group_id and group_id in group_messages:
                    current_message = group_messages[group_id]
                    response_text = f"📝 目前的自訂文案：\n{current_message}\n\n💡 修改文案：\n@message 新的文案內容\n\n🔄 恢復預設：\n@message reset"
                else:
                    response_text = """📝 設定自訂提醒文案

🔧 指令格式：
@message 自訂文案內容

💡 可用佔位符：
• {name} - 負責人姓名
• {date} - 日期 (MM/DD)  
• {weekday} - 星期

📋 文案範例：
@message 📋 今天 {date} ({weekday}) 輪到 {name} 值日！
@message 🧹 {name}，該打掃辦公室了！({date})
@message ⚡ {weekday} 提醒：{name} 負責設備檢查

🔄 恢復預設文案：
@message reset"""
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 添加成員到指定週 - 格式: @addmember 1 成員名
        if event.message.text.strip().startswith("@addmember"):
            import re
            m = re.match(r"@addmember (\d+) (.+)", event.message.text.strip())
            if m:
                week_num = int(m.group(1))
                member_name = m.group(2).strip()
                
                result = add_member_to_week(week_num, member_name)
                
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"{'✅' if result['success'] else '❌'} {result['message']}")]
                )
                messaging_api.reply_message(req)
            else:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式錯誤，請輸入 @addmember 週數 成員名\n例如: @addmember 1 Alice")]
                )
                messaging_api.reply_message(req)
        
        # 從指定週移除成員 - 格式: @removemember 1 成員名
        if event.message.text.strip().startswith("@removemember"):
            import re
            m = re.match(r"@removemember (\d+) (.+)", event.message.text.strip())
            if m:
                week_num = int(m.group(1))
                member_name = m.group(2).strip()
                
                result = remove_member_from_week(week_num, member_name)
                
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"{'✅' if result['success'] else '❌'} {result['message']}")]
                )
                messaging_api.reply_message(req)
            else:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式錯誤，請輸入 @removemember 週數 成員名\n例如: @removemember 1 Alice")]
                )
                messaging_api.reply_message(req)
        
        # 重置基準日期
        if event.message.text.strip() == "@reset_date":
            global base_date
            old_base_date = base_date
            base_date = date.today()
            save_base_date(base_date)
            
            response_text = f"🔄 基準日期已重置\n"
            response_text += f"舊基準日期: {old_base_date.strftime('%Y-%m-%d') if old_base_date else '未設定'}\n"
            response_text += f"新基準日期: {base_date.strftime('%Y-%m-%d')}\n\n"
            response_text += f"💡 從今天開始重新計算週數輪值"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 幫助指令
        if event.message.text.strip().startswith("@help"):
            parts = event.message.text.strip().split(maxsplit=1)
            if len(parts) == 1:
                # @help - 顯示總覽
                help_text = get_help_message()
            elif parts[1] == "examples":
                # @help examples - 顯示範例
                help_text = get_command_examples()
            else:
                # @help 類別 - 顯示特定類別
                category = parts[1].lower()
                if category in ["schedule", "members", "groups"]:
                    help_text = get_help_message(category)
                else:
                    help_text = "❌ 未知類別，請輸入：\n@help schedule\n@help members\n@help groups\n@help examples"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=help_text)]
            )
            messaging_api.reply_message(req)

@handler.add(JoinEvent)
def handle_join(event):
    """處理 Bot 加入群組事件，自動記錄群組 ID"""
    try:
        # 取得群組 ID
        group_id = event.source.group_id
        
        # 載入現有的群組 ID 列表
        global group_ids
        
        # 檢查是否已經存在
        if group_id not in group_ids:
            group_ids.append(group_id)
            save_group_ids()
            
            # 發送歡迎訊息並告知群組 ID 已記錄
            welcome_msg = f"""🤖 歡迎使用輪值提醒 Bot！

🚀 快速開始：
@cron mon,thu 18:00 - 設定提醒星期和時間
@week 1 姓名1,姓名2 - 設定輪值成員
@message 今天輪到{{name}}值日！ - 自訂提醒文案（選用）
@help - 查看完整指令

💡 提示：所有設定都會自動儲存，重啟後不會遺失！"""
            
            from linebot.v3.messaging.models import PushMessageRequest
            req = PushMessageRequest(
                to=group_id,
                messages=[TextMessage(text=welcome_msg)]
            )
            messaging_api.push_message(req)
            
            print(f"Bot 加入新群組，已記錄群組 ID: {group_id}")
        else:
            print(f"Bot 重新加入已知群組: {group_id}")
            
    except Exception as e:
        print(f"處理 Bot 加入群組事件時發生錯誤: {e}")

@handler.add(LeaveEvent)
def handle_leave(event):
    """處理 Bot 離開群組事件，自動移除群組 ID"""
    try:
        # 取得群組 ID
        group_id = event.source.group_id
        
        # 載入現有的群組 ID 列表
        global group_ids
        
        # 檢查並移除群組 ID
        if group_id in group_ids:
            group_ids.remove(group_id)
            save_group_ids()
            print(f"Bot 離開群組，已移除群組 ID: {group_id}")
        else:
            print(f"Bot 離開未知群組: {group_id}")
            
    except Exception as e:
        print(f"處理 Bot 離開群組事件時發生錯誤: {e}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
