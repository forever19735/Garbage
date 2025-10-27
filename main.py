from flask import Flask, request, abort
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging.models import PushMessageRequest, TextMessage
from linebot.v3.webhooks import TextMessageContent
import os
import json

# 載入 .env 檔案中的環境變數（僅在本地開發時使用）
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG: .env 檔案已載入")
except ImportError:
    # 在生產環境中（如 Railway）沒有 python-dotenv，直接忽略
    print("DEBUG: 未安裝 python-dotenv，跳過 .env 檔案載入")
    pass

app = Flask(__name__)

# 持久化檔案路徑
GROUP_IDS_FILE = "group_ids.json"
GROUPS_FILE = "groups.json"

# ===== 持久化功能 =====
def load_group_ids():
    """從檔案載入群組 ID 列表"""
    try:
        if os.path.exists(GROUP_IDS_FILE):
            with open(GROUP_IDS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"DEBUG: 已載入 {len(data)} 個群組 ID")
                return data
    except Exception as e:
        print(f"DEBUG: 載入群組 ID 檔案時發生錯誤: {e}")
    return []

def save_group_ids():
    """將群組 ID 列表儲存到檔案"""
    try:
        with open(GROUP_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(group_ids, f, ensure_ascii=False, indent=2)
        print(f"DEBUG: 已儲存 {len(group_ids)} 個群組 ID 到檔案")
    except Exception as e:
        print(f"DEBUG: 儲存群組 ID 檔案時發生錯誤: {e}")

def load_groups():
    """從檔案載入成員群組資料"""
    try:
        if os.path.exists(GROUPS_FILE):
            with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"DEBUG: 已載入 {len(data)} 週的成員資料")
                return data
    except Exception as e:
        print(f"DEBUG: 載入成員群組檔案時發生錯誤: {e}")
    return {}

def save_groups():
    """將成員群組資料儲存到檔案"""
    try:
        with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=2)
        print(f"DEBUG: 已儲存 {len(groups)} 週的成員資料到檔案")
    except Exception as e:
        print(f"DEBUG: 儲存成員群組檔案時發生錯誤: {e}")

# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 載入持久化的群組 ID 列表
group_ids = load_group_ids()
groups = load_groups()  # 儲存每週的成員名單

# 從環境變數載入已知的群組 ID
if os.getenv("LINE_GROUP_ID"):
    # 正確解析環境變數中的群組 ID（支援多個群組，以逗號分隔）
    env_group_ids = [gid.strip() for gid in os.getenv("LINE_GROUP_ID").split(",") if gid.strip()]
    group_ids.extend(env_group_ids)


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
    print("- LINE_GROUP_ID (可選，可透過 @debug 指令自動取得)")
    
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
def get_current_group():
    """
    取得當前週的成員群組
    
    Returns:
        list: 當前週的成員列表
    """
    if not isinstance(groups, dict) or len(groups) == 0:
        return []
    
    today = date.today()
    week_num = today.isocalendar()[1]  # 第幾週
    total_weeks = len(groups)
    current_week = (week_num - 1) % total_weeks + 1
    
    week_key = str(current_week)
    return groups.get(week_key, [])

# ===== 成員輪值管理函數 =====
def get_member_schedule():
    """
    取得目前的成員輪值安排
    
    Returns:
        dict: 包含成員輪值資訊的字典
    """
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        return {
            "total_weeks": 0,
            "current_week": 1,
            "weeks": []
        }
    
    total_weeks = len(groups)
    current_week = (date.today().isocalendar()[1] - 1) % max(1, total_weeks) + 1
    
    schedule_info = {
        "total_weeks": total_weeks,
        "current_week": current_week,
        "weeks": []
    }
    
    for week_key in sorted(groups.keys(), key=lambda x: int(x)):
        week_num = int(week_key)
        week_members = groups[week_key]
        week_info = {
            "week": week_num,
            "members": week_members.copy(),
            "member_count": len(week_members),
            "is_current": week_num == current_week
        }
        schedule_info["weeks"].append(week_info)
    
    return schedule_info

def update_member_schedule(week_num, members):
    """
    更新指定週的成員安排
    
    Args:
        week_num (int): 週數 (1-based)
        members (list): 成員列表
        
    Returns:
        dict: 操作結果
    """
    global groups
    
    if not isinstance(week_num, int) or week_num < 1:
        return {"success": False, "message": "週數必須是大於 0 的整數"}
    
    if not isinstance(members, list) or len(members) == 0:
        return {"success": False, "message": "成員列表不能為空"}
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        groups = {}
    
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
    global groups
    
    if not isinstance(week_num, int) or week_num < 1:
        return {"success": False, "message": "週數必須是大於 0 的整數"}
    
    if not member_name or not isinstance(member_name, str):
        return {"success": False, "message": "成員名稱不能為空"}
    
    # 確保 groups 是字典格式
    if not isinstance(groups, dict):
        groups = {}
    
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

def get_member_schedule_summary():
    """
    取得成員輪值的簡要摘要，用於顯示給使用者
    
    Returns:
        str: 格式化的成員輪值摘要字串
    """
    schedule = get_member_schedule()
    
    if schedule["total_weeks"] == 0:
        return "👥 尚未設定成員輪值表\n\n💡 使用「成員設定 1 小明 小華」來設定第1週的成員"
    
    summary = f"👥 垃圾收集成員輪值表\n\n"
    summary += f"📅 總共 {schedule['total_weeks']} 週輪值\n"
    summary += f"📍 目前第 {schedule['current_week']} 週\n\n"
    
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
    清空所有成員輪值安排
    
    Returns:
        dict: 操作結果
    """
    global groups
    
    old_count = len(groups) if isinstance(groups, dict) else 0
    groups = {}
    save_groups()  # 立即儲存到檔案
    
    return {
        "success": True,
        "message": f"已清空所有成員輪值安排 (原有 {old_count} 週資料)",
        "cleared_weeks": old_count
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
    重置所有資料 (成員安排 + 群組 ID)
    
    Returns:
        dict: 操作結果
    """
    global groups, group_ids
    
    # 記錄原始資料
    old_groups_count = len(groups) if isinstance(groups, dict) else 0
    old_group_ids_count = len(group_ids)
    
    # 清空所有資料
    groups = {}
    group_ids = []
    
    # 儲存變更
    save_groups()
    save_group_ids()
    
    return {
        "success": True,
        "message": f"已重置所有資料 (清空 {old_groups_count} 週成員安排 + {old_group_ids_count} 個群組 ID)",
        "cleared_groups": old_groups_count,
        "cleared_group_ids": old_group_ids_count
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
    
    # 成員輪值狀態
    status += f"👥 成員輪值:\n"
    status += f"  └ 總週數: {groups_info['total_weeks']}\n"
    status += f"  └ 目前週: {groups_info['current_week']}\n\n"
    
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
        category (str): 指定類別 ('schedule', 'members', 'groups', 'test')
        
    Returns:
        str: 格式化的幫助訊息
    """
    
    if category == "schedule":
        return """⏰ 排程管理指令

🕐 查看排程：
@schedule - 顯示目前推播排程

⚙️ 設定排程：
@settime HH:MM - 設定推播時間
範例：@settime 18:30

@setday 星期 - 設定推播星期
範例：@setday mon,thu

@setcron 星期 時 分 - 同時設定星期和時間
範例：@setcron tue,fri 20 15

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
@setweek 週數 成員1,成員2 - 設定整週成員
範例：@setweek 1 Alice,Bob,Charlie

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

🔍 查看群組：
@groups - 顯示已設定的群組列表
@info - 顯示詳細群組資訊

⚙️ 管理群組：
@debug - 自動添加當前群組 ID
💡 在想要接收提醒的群組中輸入此指令

�️ 清空功能：
@clear_groups - 清空所有群組 ID

�📊 群組資訊說明：
- 每個群組只需執行一次 @debug
- 支援多個群組同時接收提醒
- 群組 ID 以 'C' 開頭"""

    elif category == "test":
        return """🧪 查看和調試指令

📊 查看資訊：
@status - 完整系統狀態摘要
@schedule - 排程資訊
@members - 成員輪值表
@groups - 群組列表
@info - 詳細群組資訊

🆘 獲取幫助：
@help - 顯示所有指令
@help 類別 - 顯示特定類別指令
類別：schedule, members, groups, manage, test"""

    elif category == "manage":
        return """🔧 管理和重置指令

🗑️ 清空功能：
@clear_week 週數 - 清空指定週的成員
範例：@clear_week 1

@clear_members - 清空所有週的成員安排
@clear_groups - 清空所有群組 ID

🔄 重置功能：
@reset_all - 重置所有資料 (成員+群組)
⚠️ 此操作無法復原，請謹慎使用

📊 系統管理：
@status - 查看完整系統狀態
包含：成員輪值狀態、群組狀態、排程狀態

💡 管理建議：
- 使用 @status 確認操作前的狀態
- 漸進式清空：先清空特定週，再考慮全部清空
- 重要資料請先記錄再執行重置
- 清空操作會立即生效並持久化"""

    else:  # 顯示所有指令概覽
        return """🤖 垃圾收集提醒 Bot 指令大全

📋 分類查看：
@help schedule - 排程管理指令 (設定提醒時間)
@help members - 成員管理指令 (輪值安排)
@help groups - 群組管理指令 (LINE 群組設定)
@help manage - 管理重置指令 (清空/重置功能)
@help test - 查看調試指令 (狀態查看)

🔥 常用指令：
@schedule - 查看推播排程
@members - 查看成員輪值表
@groups - 查看群組設定
@status - 查看系統狀態
@debug - 添加群組 ID

⚙️ 快速設定：
@settime 18:30 - 設定推播時間
@setday mon,thu - 設定推播星期
@setcron mon,thu 18 30 - 同時設定星期和時間
@setweek 1 Alice,Bob - 設定第1週成員

👥 成員管理：
@addmember 1 Charlie - 添加成員到第1週
@removemember 1 Alice - 從第1週移除成員
@clear_week 1 - 清空第1週成員
@clear_members - 清空所有成員

📱 群組管理：
@info - 顯示詳細群組資訊
@clear_groups - 清空所有群組 ID

🔄 管理功能：
@status - 查看完整系統狀態
@reset_all - 重置所有資料 (謹慎使用)

💡 使用提示：
- 所有時間都是台北時間
- 群組 ID 會自動記住
- 支援多群組推播
- 成員輪值自動循環
- 所有設定都會持久化儲存

❓ 需要詳細說明請輸入：
@help 類別名稱

🏃‍♂️ 新手快速開始：
1. 在群組中輸入 @debug (添加群組)
2. 輸入 @settime 18:00 (設定提醒時間)
3. 輸入 @setweek 1 姓名1,姓名2 (設定成員)
4. 輸入 @status (查看設定狀態)"""

def get_command_examples():
    """
    取得指令範例
    
    Returns:
        str: 格式化的指令範例
    """
    return """📚 指令範例集

🏃‍♂️ 快速開始：
1. @debug - 在群組中添加群組 ID
2. @settime 18:00 - 設定晚上6點推播
3. @setweek 1 Alice,Bob - 設定第1週成員
4. @status - 查看設定狀態

⏰ 排程設定範例：
@settime 07:30 - 早上7:30提醒
@settime 18:00 - 晚上6:00提醒
@setday mon,wed,fri - 週一三五提醒
@setcron sat,sun 09 00 - 週末早上9:00

👥 成員管理範例：
@setweek 1 小明,小華 - 第1週：小明、小華
@setweek 2 小美,小強 - 第2週：小美、小強
@addmember 1 小李 - 第1週加入小李
@removemember 2 小強 - 第2週移除小強

📱 多群組設定：
在群組A輸入：@debug
在群組B輸入：@debug
兩個群組都會收到提醒

🧪 驗證流程：
@members - 查看輪值安排
@schedule - 確認推播時間  
@status - 查看系統狀態
@groups - 確認群組設定

💡 實用技巧：
- 用表情符號標記成員：@setweek 1 Alice🌟,Bob🔥
- 設定備用成員：@setweek 3 主要成員,備用成員
- 查看下次提醒：@schedule"""

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
def get_schedule_info():
    """
    取得目前設定的推播排程資訊
    
    Returns:
        dict: 包含排程資訊的字典
    """
    global job
    
    if not job:
        return {
            "is_configured": False,
            "message": "排程未設定",
            "next_run_time": None,
            "schedule_details": None
        }
    
    try:
        # 下次執行時間
        next_run = job.next_run_time
        next_run_str = next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else "未知"
        
        # 從 job 的觸發器取得資訊
        trigger = job.trigger
        
        # 取得基本資訊
        schedule_details = {
            "timezone": "Asia/Taipei",
            "trigger_type": str(type(trigger).__name__)
        }
        
        # 嘗試從觸發器字串解析資訊
        trigger_str = str(trigger)
        
        # 解析 CronTrigger 資訊 (例如: "cron[day_of_week='mon,thu', hour='17', minute='10']")
        if "day_of_week=" in trigger_str:
            import re
            
            # 解析星期
            day_match = re.search(r"day_of_week='([^']+)'", trigger_str)
            if day_match:
                days_str = day_match.group(1)
                # 處理兩種格式：數字格式 (1,4) 和字母格式 (mon,thu)
                if days_str.replace(',', '').replace(' ', '').isdigit():
                    # 數字格式
                    days_numbers = days_str.split(',')
                    day_names = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
                    days = []
                    for day_num in days_numbers:
                        try:
                            idx = int(day_num.strip())
                            if 0 <= idx <= 6:
                                days.append(day_names[idx])
                        except (ValueError, IndexError):
                            pass
                    schedule_details["days"] = ','.join(days) if days else "未知"
                else:
                    # 字母格式，直接使用
                    schedule_details["days"] = days_str
            
            # 解析小時
            hour_match = re.search(r"hour='([^']+)'", trigger_str)
            if hour_match:
                try:
                    hour = int(hour_match.group(1))
                    schedule_details["hour"] = hour
                except ValueError:
                    schedule_details["hour"] = None
            
            # 解析分鐘
            minute_match = re.search(r"minute='([^']+)'", trigger_str)
            if minute_match:
                try:
                    minute = int(minute_match.group(1))
                    schedule_details["minute"] = minute
                except ValueError:
                    schedule_details["minute"] = None
        
        # 格式化時間顯示
        if "hour" in schedule_details and "minute" in schedule_details:
            hour = schedule_details.get("hour")
            minute = schedule_details.get("minute")
            if hour is not None and minute is not None:
                schedule_details["time"] = f"{hour:02d}:{minute:02d}"
            else:
                schedule_details["time"] = "未設定"
        else:
            schedule_details["time"] = "未設定"
        
        # 建立 cron 表達式
        minute_val = schedule_details.get("minute", "*")
        hour_val = schedule_details.get("hour", "*")
        days_val = schedule_details.get("days", "*")
        
        cron_expr = f"{minute_val} {hour_val} * * {days_val}"
        
        return {
            "is_configured": True,
            "message": "排程已設定",
            "next_run_time": next_run_str,
            "schedule_details": schedule_details,
            "cron_expression": cron_expr,
            "raw_trigger": trigger_str
        }
        
    except Exception as e:
        return {
            "is_configured": False,
            "message": f"無法解析排程資訊: {str(e)}",
            "next_run_time": None,
            "schedule_details": None,
            "error": str(e)
        }

def update_schedule(days=None, hour=None, minute=None):
    """
    更新推播排程設定
    
    Args:
        days (str): 星期設定，例如 "mon,thu"
        hour (int): 小時 (0-23)
        minute (int): 分鐘 (0-59)
        
    Returns:
        dict: 操作結果
    """
    global job
    
    try:
        # 取得目前設定
        current_info = get_schedule_info()
        
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
        if job:
            job.remove()
        
        # 建立新排程，明確指定時區
        from apscheduler.triggers.cron import CronTrigger
        job = scheduler.add_job(
            send_trash_reminder, 
            CronTrigger(
                day_of_week=days, 
                hour=hour, 
                minute=minute,
                timezone=pytz.timezone('Asia/Taipei')  # 明確指定時區
            )
        )
        
        return {
            "success": True,
            "message": f"推播時間已更新為 {days} {hour:02d}:{minute:02d}",
            "schedule": {
                "days": days,
                "time": f"{hour:02d}:{minute:02d}",
                "next_run": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else "未知"
            }
        }
        
    except Exception as e:
        return {"success": False, "message": f"更新排程失敗: {str(e)}", "error": str(e)}

def get_schedule_summary():
    """
    取得排程的簡要摘要，用於顯示給使用者
    
    Returns:
        str: 格式化的排程摘要字串
    """
    info = get_schedule_info()
    
    if not info["is_configured"]:
        return "❌ 排程未設定"
    
    details = info["schedule_details"]
    if not details:
        return "❌ 無法取得排程詳情"
    
    # 格式化星期顯示
    days = details.get("days", "未知")
    day_mapping = {
        "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
        "fri": "週五", "sat": "周六", "sun": "週日"
    }
    
    if "," in days:
        day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
        days_chinese = "、".join(day_list)
    else:
        days_chinese = day_mapping.get(days, days)
    
    time_str = details.get("time", "未知")
    timezone_str = details.get("timezone", "未知")
    next_run = info.get("next_run_time", "未知")
    
    # 計算距離下次執行的時間
    from datetime import datetime
    import pytz
    
    try:
        taipei_tz = pytz.timezone('Asia/Taipei')
        now = datetime.now(taipei_tz)
        
        # 解析下次執行時間
        if job and job.next_run_time:
            # job.next_run_time 已經是有時區的 datetime 物件
            time_diff = job.next_run_time - now
            total_seconds = time_diff.total_seconds()
            
            if total_seconds > 0:
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                
                if hours > 24:
                    days = hours // 24
                    hours = hours % 24
                    time_until = f"{days} 天 {hours} 小時 {minutes} 分鐘"
                elif hours > 0:
                    time_until = f"{hours} 小時 {minutes} 分鐘"
                else:
                    time_until = f"{minutes} 分鐘"
            else:
                time_until = "即將執行"
        else:
            time_until = "無法計算"
    except Exception as e:
        time_until = f"計算錯誤: {str(e)}"
    
    summary = f"""📅 垃圾收集提醒排程

🕐 執行時間: {time_str} ({timezone_str})
📆 執行星期: {days_chinese}
⏰ 下次執行: {next_run}
⏳ 距離下次: {time_until}

✅ 排程狀態: 已啟動"""
    
    return summary

def send_trash_reminder():
    today = date.today()
    weekday = today.weekday()  # 0=週一, 1=週二, ..., 6=週日
    weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
    print(f"DEBUG: 今天是 {today.strftime('%m/%d')}, {weekday_names[weekday]} (weekday={weekday})")
    
    # 移除週一四限制，根據排程執行
    group = get_current_group()
    print(f"DEBUG: 當前群組成員: {group}")
    
    if not group:
        message = f"🗑️ 今天 {today.strftime('%m/%d')} ({weekday_names[weekday]}) 是收垃圾日！\n💡 請設定成員輪值表"
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
        
        message = f"🗑️ 今天 {today.strftime('%m/%d')} ({weekday_names[weekday]}) 輪到 {person} 收垃圾！"
    
    print(f"DEBUG: 準備推播訊息: {message}")
    print(f"DEBUG: 群組 IDs: {group_ids}")

    if not group_ids:
        print("DEBUG: 沒有設定任何群組 ID，無法推播")
        print("DEBUG: 請在群組中輸入 @debug 指令來自動添加群組 ID")
        return

    for gid in group_ids:
        # 驗證群組 ID 格式並詳細記錄
        print(f"DEBUG: 檢查群組 ID: '{gid}' (長度: {len(gid) if gid else 0})")
        
        if not gid:
            print(f"DEBUG: 群組 ID 為空")
            continue
            
        if not isinstance(gid, str):
            print(f"DEBUG: 群組 ID 不是字串類型: {type(gid)}")
            continue
            
        if not gid.startswith("C"):
            print(f"DEBUG: 群組 ID 不以 'C' 開頭: {gid}")
            continue
            
        if len(gid) <= 10:
            print(f"DEBUG: 群組 ID 長度不足 (需要 > 10): {len(gid)}")
            continue
            
        # 群組 ID 格式正確，開始推播
        print(f"DEBUG: 推播到群組 {gid}")
        try:
            # 檢查 messaging_api 是否已初始化
            if not messaging_api:
                print("DEBUG: MessagingApi 未初始化，請檢查 LINE_CHANNEL_ACCESS_TOKEN")
                continue
                
            req = PushMessageRequest(
                to=gid,
                messages=[TextMessage(text=message)]
            )
            print(f"DEBUG: 建立推播請求: to={gid}, message_length={len(message)}")
            
            response = messaging_api.push_message(req)
            print(f"DEBUG: 推播成功 - Response: {response}")
        except Exception as e:
            print(f"DEBUG: 推播失敗 - {type(e).__name__}: {e}")
            # 特別處理 LINE API 錯誤
            if "invalid" in str(e).lower() and "to" in str(e).lower():
                print(f"DEBUG: 群組 ID '{gid}' 可能無效或 Bot 未加入該群組")
                print(f"DEBUG: 請確認:")
                print(f"DEBUG: 1. Bot 已加入群組 {gid}")
                print(f"DEBUG: 2. 群組 ID 正確 (可用 @debug 指令重新取得)")
            import traceback
            print(f"DEBUG: 完整錯誤: {traceback.format_exc()}")
    
    print(message)

# ===== 啟動排程（每週一、四下午 5:10）=====
from apscheduler.triggers.cron import CronTrigger
import pytz
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
job = scheduler.add_job(
    send_trash_reminder, 
    CronTrigger(
        day_of_week="mon,thu", 
        hour=17, 
        minute=10,
        timezone=pytz.timezone('Asia/Taipei')  # 明確指定時區
    )
)
scheduler.start()

print(f"DEBUG: 排程已啟動，下次執行時間: {job.next_run_time}")
print(f"DEBUG: 當前時間: {pytz.timezone('Asia/Taipei').localize(datetime.now())}")

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

#     if text == "@debug":
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
    global job
    # 使用者設定推播星期、時、分指令
    if event.message.text.strip().startswith("@setcron"):
        import re
        m = re.match(r"@setcron ([a-z,]+) (\d{1,2}) (\d{1,2})", event.message.text.strip())
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
            
            # 移除舊排程並建立新排程，明確指定時區
            job.remove()
            job = scheduler.add_job(
                send_trash_reminder, 
                CronTrigger(
                    day_of_week=days, 
                    hour=hour, 
                    minute=minute,
                    timezone=pytz.timezone('Asia/Taipei')  # 明確指定時區
                )
            )
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"✅ 推播時間已更新為 {days} {hour:02d}:{minute:02d} (台北時間)\n⏰ 下次執行: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")]
            )
            messaging_api.reply_message(req)
        else:
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="格式錯誤，請輸入 @setcron mon,thu 18 30")]
            )
            messaging_api.reply_message(req)

    # 使用者設定推播星期指令
    if event.message.text.strip().startswith("@setday"):
        import re
        m = re.match(r"@setday ([a-z,]+)", event.message.text.strip())
        if m:
            days = m.group(1)
            # 取得目前排程時間
            current_info = get_schedule_info()
            if current_info["is_configured"] and current_info["schedule_details"]:
                hour = current_info["schedule_details"]["hour"]
                minute = current_info["schedule_details"]["minute"]
            else:
                hour = 17  # 預設值
                minute = 10  # 預設值
            
            job.remove()
            job = scheduler.add_job(
                send_trash_reminder, 
                CronTrigger(
                    day_of_week=days, 
                    hour=hour, 
                    minute=minute,
                    timezone=pytz.timezone('Asia/Taipei')  # 明確指定時區
                )
            )
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"✅ 推播星期已更新為 {days}\n⏰ 下次執行: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")]
            )
            messaging_api.reply_message(req)
        else:
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="格式錯誤，請輸入 @setday mon,thu")]
            )
            messaging_api.reply_message(req)

    if getattr(event.message, "type", None) == "text":
        print("收到訊息:", event.message.text)
        print("來源:", event.source)

        # 使用者設定推播時間指令
        if event.message.text.strip().startswith("@settime"):
            import re
            m = re.match(r"@settime (\d{1,2}):(\d{2})", event.message.text.strip())
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
                
                # 取得目前的星期設定
                current_info = get_schedule_info()
                if current_info["is_configured"] and current_info["schedule_details"]:
                    days = current_info["schedule_details"]["days"]
                else:
                    days = "mon,thu"  # 預設值
                
                job.remove()
                job = scheduler.add_job(
                    send_trash_reminder, 
                    CronTrigger(
                        day_of_week=days, 
                        hour=hour, 
                        minute=minute,
                        timezone=pytz.timezone('Asia/Taipei')  # 明確指定時區
                    )
                )
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"✅ 推播時間已更新為 {hour:02d}:{minute:02d} (台北時間)\n⏰ 下次執行: {job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")]
                )
                messaging_api.reply_message(req)
            else:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式錯誤，請輸入 @settime HH:MM")]
                )
                messaging_api.reply_message(req)

        if event.message.text.strip() == "@debug":
            gid = getattr(event.source, "group_id", None)
            if gid:
                # 使用新的函數添加群組 ID
                result = add_line_group_id(gid)
                if result["success"]:
                    print(f"DEBUG: 新增群組 ID: {gid}")
                    response_text = f"✅ 群組ID已添加：{gid}\n目前已設定的群組: {result['total_groups']} 個"
                else:
                    response_text = f"ℹ️ {result['message']}\n目前已設定的群組: {len(group_ids)} 個"
                
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_text)]
                )
                messaging_api.reply_message(req)
            else:
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這不是群組，無法取得群組 ID。")]
                )
                messaging_api.reply_message(req)
        
        # 顯示目前已設定的群組列表
        if event.message.text.strip() == "@groups":
            if group_ids:
                group_list = "\n".join([f"{i+1}. {gid}" for i, gid in enumerate(group_ids)])
                response_text = f"📋 目前已設定的群組 ({len(group_ids)} 個):\n{group_list}"
            else:
                response_text = "❌ 尚未設定任何群組 ID\n請在群組中輸入 @debug 來添加群組 ID"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 顯示詳細的群組 ID 資訊
        if event.message.text.strip() == "@info":
            group_info = get_line_group_ids()
            
            if group_info["is_configured"]:
                valid_count = len(group_info["valid_ids"])
                invalid_count = group_info["count"] - valid_count
                
                response_text = f"📊 群組 ID 詳細資訊：\n\n"
                response_text += f"總群組數：{group_info['count']}\n"
                response_text += f"有效群組：{valid_count}\n"
                if invalid_count > 0:
                    response_text += f"無效群組：{invalid_count}\n"
                
                response_text += f"\n📋 群組列表：\n"
                for i, gid in enumerate(group_info["group_ids"], 1):
                    status = "✅" if gid in group_info["valid_ids"] else "❌"
                    response_text += f"{i}. {status} {gid}\n"
            else:
                response_text = "❌ 尚未設定任何群組 ID\n請在群組中輸入 @debug 來添加群組 ID"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 顯示推播排程資訊
        if event.message.text.strip() == "@schedule":
            schedule_info = get_schedule_info()
            
            if schedule_info["is_configured"]:
                details = schedule_info["schedule_details"]
                response_text = f"⏰ 目前推播排程：\n\n"
                response_text += f"📅 星期：{details['days']}\n"
                response_text += f"🕐 時間：{details['time']}\n"
                response_text += f"🌏 時區：{details['timezone']}\n"
                response_text += f"📋 Cron：{schedule_info['cron_expression']}\n\n"
                response_text += f"⏭️ 下次執行：\n{schedule_info['next_run_time']}"
            else:
                response_text = f"❌ {schedule_info['message']}"
                if "error" in schedule_info:
                    response_text += f"\n錯誤：{schedule_info['error']}"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
            messaging_api.reply_message(req)
        
        # 顯示成員輪值表
        if event.message.text.strip() == "@members":
            summary = get_member_schedule_summary()
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
        
        # 設定指定週的成員 - 格式: @setweek 1 成員1,成員2
        if event.message.text.strip().startswith("@setweek"):
            import re
            m = re.match(r"@setweek (\d+) (.+)", event.message.text.strip())
            if m:
                week_num = int(m.group(1))
                members_str = m.group(2)
                members = [member.strip() for member in members_str.split(",") if member.strip()]
                
                result = update_member_schedule(week_num, members)
                
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
                    messages=[TextMessage(text="格式錯誤，請輸入 @setweek 週數 成員1,成員2\n例如: @setweek 1 Alice,Bob")]
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
                if category in ["schedule", "members", "groups", "test"]:
                    help_text = get_help_message(category)
                else:
                    help_text = "❌ 未知類別，請輸入：\n@help schedule\n@help members\n@help groups\n@help test\n@help examples"
            
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=help_text)]
            )
            messaging_api.reply_message(req)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
