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
# 從 Container 獲取服務
firebase_repository = container.firebase_repository
member_service = container.member_service
# notification_service 和 schedule_service 稍後在排程啟動後可用

app = Flask(__name__)


# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 從環境變數載入已知的群組 ID（補充載入）到 MemberService
if os.getenv("LINE_GROUP_ID"):
    env_group_ids = [gid.strip() for gid in os.getenv("LINE_GROUP_ID").split(",") if gid.strip()]
    for gid in env_group_ids:
        member_service.add_group(gid)
        print(f"✅ 從 LINE_GROUP_ID 補充載入群組: {gid}")


print("ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
print("CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
print("GROUP_ID:", member_service.group_ids)
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

# ===== 啟動排程（每週一、四下午 5:10）=====
from apscheduler.triggers.cron import CronTrigger
import pytz
from services.notification_service import NotificationService

scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
group_jobs = {}  # 儲存每個群組的推播任務

# 初始化 Container 的 Scheduler 相關服務
container.init_scheduler(scheduler, group_jobs)
schedule_service = container.schedule_service
notification_service = container.notification_service

# 初始化群組排程
schedule_service.initialize_jobs(notification_service.send_group_reminder)

# 確保所有已知群組都有預設排程
for gid in member_service.group_ids:
    if gid not in schedule_service.group_schedules:
        print(f"為群組 {gid} 設定預設排程")
        schedule_service.update_schedule(gid, "mon,thu", 17, 10, notification_service.send_group_reminder)

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
    context = create_command_context(
        event=event,
        group_id=group_id,
        # 服務
        member_service=member_service,
        schedule_service=schedule_service,
        firebase_service=firebase_service.firebase_service_instance,
        # 資料 (不再傳入全域變數，而是傳入 Services)
        groups=member_service.groups,
        group_schedules=schedule_service.group_schedules,
        group_messages=member_service.group_messages,
        base_date=member_service.base_date,
        # 回調函數 - 代理到 Services
        reminder_callback=notification_service.send_group_reminder,
        update_schedule=lambda gid, d, h, m: schedule_service.update_schedule(gid, d, h, m, reminder_callback=notification_service.send_group_reminder),
        update_member_schedule=member_service.update_member_schedule,
        get_member_schedule_summary=member_service.get_member_schedule_summary,
        get_schedule_summary=schedule_service.get_schedule_summary,
        get_system_status=None, # 已移除
        add_member_to_week=member_service.add_member_to_week,
        remove_member_from_week=member_service.remove_member_from_week,
        clear_week_members=member_service.clear_week_members,
        clear_all_members=member_service.clear_all_members,
        clear_all_group_ids=member_service.clear_all_group_ids,
        reset_all_data=None, # 已移除
        save_base_date=lambda d: setattr(member_service, 'base_date', d),
        save_group_messages=lambda data: setattr(member_service, 'group_messages', data),
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
        
        # 使用 MemberService 加入群組
        is_new = member_service.add_group(group_id)
        
        if is_new:
            # 發送歡迎訊息
            notification_service.send_welcome_message(group_id)
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
        
        # 使用 MemberService 移除群組
        if member_service.remove_group(group_id):
            print(f"Bot 離開群組，已移除群組 ID: {group_id}")
        else:
            print(f"Bot 離開未知群組: {group_id}")
            
    except Exception as e:
        print(f"處理 Bot 離開群組事件時發生錯誤: {e}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
