from flask import Flask, request, abort
from datetime import date, datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging.models import PushMessageRequest, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import TextMessageContent, JoinEvent, LeaveEvent
import os
import json
import requests
import firebase_service

from handlers import MessageHandler, normalize_command, suggest_commands
from commands.handler import handle_command, create_command_context, is_known_command
from config import COMMAND_ALIASES, AVAILABLE_COMMANDS, ERROR_TEMPLATES, get_command_description

# ===== Container =====
from container import AppContainer

# 創建 AppContainer 實例 (Dependency Injection)
container = AppContainer()
# 從 Container 獲取服務
firebase_repository = container.firebase_repository
member_service = container.member_service
# schedule_service 需要 scheduler，在後面初始化
schedule_service = None

app = Flask(__name__)


# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 載入持久化的資料
# 載入持久化的資料
group_ids = firebase_repository.load_data('group_ids', [])
# group_schedules 暫時載入，稍後由 ScheduleService 管理
group_schedules = firebase_repository.load_data('group_schedules', {})
group_messages = firebase_repository.load_data('group_messages', {})

# 從環境變數載入已知的群組 ID（補充載入）
if os.getenv("LINE_GROUP_ID"):
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
    firebase_repository.save_data('group_ids', group_ids)  # 立即儲存到檔案
    
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
    global group_ids, group_schedules
    
    # 記錄原始資料
    old_group_ids_count = len(group_ids)
    old_schedules_count = len(group_schedules) if isinstance(group_schedules, dict) else 0
    
    # 清空成員資料
    member_reset_result = member_service.clear_all_members()
    
    # 清空其他資料
    group_ids = []
    group_schedules = {}
    
    # 儲存變更
    firebase_repository.save_data('group_ids', group_ids)
    firebase_repository.save_data('group_schedules', group_schedules)
    
    return {
        "success": True,
        "message": f"已重置所有資料 (成員資料清除: {member_reset_result.get('message')} + {old_group_ids_count} 個群組 ID + {old_schedules_count} 個排程設定)",
        "cleared_member_data": member_reset_result,
        "cleared_group_ids": old_group_ids_count,
        "cleared_schedules": old_schedules_count
    }

def get_scheduler_jobs():
    """
    取得目前排程器的工作列表
    
    Returns:
        dict: 排程器資訊
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
    """
    # 取得各種資料狀態
    groups_info = member_service.get_member_schedule()
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
        try:
            base_date_obj = datetime.fromisoformat(groups_info['base_date']).date()
        except TypeError:
             # handle case where base_date is already a date object or string parsing fails
             base_date_obj = groups_info['base_date'] if isinstance(groups_info['base_date'], date) else datetime.now().date()
            
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
        # 取得排程器運行狀態
        scheduler_jobs = get_scheduler_jobs()
        # 取得排程設定資訊
        schedule_config_summary = schedule_service.get_schedule_summary() if schedule_service else "排程服務未初始化"
        
        status += f"⏰ 排程設定:\n"
        status += f"  └ 排程器: {'運行中' if scheduler_jobs['scheduler_running'] else '已停止'}\n"
        status += f"  └ 時區: {scheduler_jobs['timezone']}\n"
        status += f"  └ 任務數量: {scheduler_jobs['job_count']}\n"
        
        if scheduler_jobs['jobs']:
            for job in scheduler_jobs['jobs']:
                status += f"  └ {job['name']}: {job['next_run']}\n"
        
        status += f"\n🕐 目前時間: {scheduler_jobs['current_time']}"
    except Exception as e:
        status += f"⏰ 排程設定:\n"
        status += f"  └ 狀態: 載入失敗 ({str(e)})\n"
        import traceback
        traceback.print_exc()
        
        # 基本時間資訊
        import pytz
        from datetime import datetime
        current_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S %Z')
        status += f"\n🕐 目前時間: {current_time}"
    
    return status

# ===== 幫助功能 =====


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
    firebase_repository.save_data('group_ids', group_ids)  # 立即儲存到檔案
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
        firebase_repository.save_data('group_ids', group_ids)  # 立即儲存到檔案
        return {
            "success": True,
            "message": f"成功移除群組 ID: {group_id}",
            "total_groups": len(group_ids)
        }
    else:
        return {"success": False, "message": f"群組 ID {group_id} 不存在"}

# ===== 推播時間管理函數 =====
# The original get_schedule_info, update_schedule, and get_schedule_summary functions are now handled by ScheduleService.

def send_group_reminder(group_id):
    """
    發送特定群組的垃圾收集提醒（支援週內按日輪值）
    
    Args:
        group_id (str): 群組ID
    """
    try:
        # 取得當前日期資訊
        from datetime import datetime
        import pytz
        import requests
        today = datetime.now(pytz.timezone('Asia/Taipei')).date()
        
        # 取得今天負責的成員（週內按日輪值）
        responsible_member = member_service.get_current_day_member(group_id, today, group_schedules)
        
        if not responsible_member:
            print(f"群組 {group_id} 今天 {today} 沒有設定負責成員")
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
        import traceback
        traceback.print_exc()

def send_trash_reminder():
    from datetime import date
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
        
        if not gid or not isinstance(gid, str) or not gid.startswith("C") or len(gid) <= 10:
             print(f"跳過無效群組 ID: {gid}")
             continue
        
        # 取得該群組的成員輪值
        group = member_service.get_current_group(gid)
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
            from linebot.v3.messaging.models import PushMessageRequest, TextMessage
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
            traceback.print_exc()
    
    print("所有群組推播處理完成")

# ===== 啟動排程（每週一、四下午 5:10）=====
from apscheduler.triggers.cron import CronTrigger
import pytz
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
group_jobs = {}  # 儲存每個群組的推播任務
# 初始化 ScheduleService (現在 scheduler 已建立)
container.init_scheduler(scheduler, group_jobs)
schedule_service = container.schedule_service

def initialize_group_schedules():
    """初始化群組排程設定"""
    global group_schedules
    
    # 為所有現有群組設定預設排程（如果尚未設定）
    for group_id in group_ids:
        if group_id not in group_schedules:
            # 設定預設排程：週一、週四 17:10
            print(f"為群組 {group_id} 設定預設排程")
            result = schedule_service.update_schedule(group_id, "mon,thu", 17, 10, send_group_reminder)
            if result["success"]:
                print(f"群組 {group_id} 預設排程設定成功")
            else:
                print(f"群組 {group_id} 預設排程設定失敗: {result['message']}")
    
    # 為已存在於 group_schedules 的群組重新建立排程任務
    for group_id, config in group_schedules.items():
        if group_id not in group_jobs:
            print(f"重新建立群組 {group_id} 的排程任務")
            result = schedule_service.update_schedule(
                group_id, 
                config.get("days", "mon,thu"),
                config.get("hour", 17), 
                config.get("minute", 10),
                send_group_reminder
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
    """處理 LINE 訊息事件"""
    
    # 檢查是否為文字訊息
    if not hasattr(event.message, 'text'):
        return
    
    # 標準化指令（支援中文別名）
    original_text = event.message.text.strip()
    normalized_text = normalize_command(original_text)
    
    # 如果標準化後不同，表示使用了別名
    if normalized_text != original_text:
        print(f"指令別名轉換: {original_text} -> {normalized_text}")
    
    # 非命令訊息不處理
    if not normalized_text.startswith('@'):
        return
    
    # ===== 使用新的命令處理架構 =====
    group_id = get_group_id_from_event(event)
    
    # 建立命令上下文
    # 建立命令上下文
    context = create_command_context(
        event=event,
        group_id=group_id,
        # 服務
        member_service=member_service,
        schedule_service=schedule_service,
        firebase_service=firebase_service.firebase_service_instance,
        # 資料
        groups=member_service.groups,
        group_schedules=schedule_service.group_schedules,
        group_messages=group_messages,
        base_date=member_service.base_date,
        # 回調函數 - 代理到 Services
        reminder_callback=send_group_reminder,
        update_schedule=lambda gid, d, h, m: schedule_service.update_schedule(gid, d, h, m, reminder_callback=send_group_reminder),
        update_member_schedule=member_service.update_member_schedule,
        get_member_schedule_summary=member_service.get_member_schedule_summary,
        get_schedule_summary=schedule_service.get_schedule_summary,
        get_system_status=get_system_status,
        add_member_to_week=member_service.add_member_to_week,
        remove_member_from_week=member_service.remove_member_from_week,
        clear_week_members=member_service.clear_week_members,
        clear_all_members=member_service.clear_all_members,
        clear_all_group_ids=clear_all_group_ids,
        reset_all_data=reset_all_data,
        save_base_date=lambda d: setattr(member_service, 'base_date', d),
        save_group_messages=lambda data: firebase_repository.save_data('group_messages', data),
    )
    
    # 嘗試使用新的命令處理器
    response = handle_command(normalized_text, context)
    
    if response is not None:
        # 新處理器成功處理，發送回覆
        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=response)]
        )
        messaging_api.reply_message(req)
        return
    
    # ===== 未知指令處理 =====
    # 如果新處理器沒有處理，表示是未知指令
    command_part = normalized_text.split()[0]
    suggestions = suggest_commands(command_part)
    message = ERROR_TEMPLATES['unknown_command'].format(
        command=command_part,
        suggestions=suggestions
    )
    
    req = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=message)]
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
            firebase_repository.save_data('group_ids', group_ids)
            
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
            firebase_repository.save_data('group_ids', group_ids)
            print(f"Bot 離開群組，已移除群組 ID: {group_id}")
        else:
            print(f"Bot 離開未知群組: {group_id}")
            
    except Exception as e:
        print(f"處理 Bot 離開群組事件時發生錯誤: {e}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
