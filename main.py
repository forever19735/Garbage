from flask import Flask, request, abort
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import JoinEvent, LeaveEvent
import os
import pytz

from handlers import normalize_command, suggest_commands
from commands.handler import handle_command, create_command_context
from config import Config, ERROR_TEMPLATES

# ===== Container =====
from container import AppContainer

# 1. 載入設定
Config.load()

# 2. 初始化容器與服務
container = AppContainer()
member_service = container.member_service
# 補充載入環境變數中的群組
for gid in Config.LINE_GROUP_ID:
    member_service.add_group(gid)

# 3. 初始化 Flask 與 LINE Bot
app = Flask(__name__)
configuration = Configuration(access_token=Config.LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

# 4. 初始化排程器
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
group_jobs = {} 
container.init_scheduler(scheduler, group_jobs)
schedule_service = container.schedule_service
notification_service = container.notification_service

# 初始化任務並確保預設排程
schedule_service.initialize_jobs(notification_service.send_group_reminder)
schedule_service.ensure_default_schedules(member_service.group_ids, notification_service.send_group_reminder)

# 啟動排程
if not scheduler.running:
    scheduler.start()

print(f"✅ Bot 啟動成功 | 排程任務: {len(group_jobs)} | 環境: {os.getenv('RAILWAY_ENVIRONMENT_NAME', 'Local')}")


@app.route("/")
def index():
    return "LINE Trash Bot is running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)
    return "OK"

# ===== 事件處理器 =====
def get_group_id_from_event(event):
    """提取群組 ID"""
    if hasattr(event.source, 'group_id'):
        return event.source.group_id
    return None

@handler.add(MessageEvent)
def handle_message(event):
    """處理 LINE 訊息事件"""
    if not hasattr(event.message, 'text'):
        return
    
    original_text = event.message.text.strip()
    normalized_text = normalize_command(original_text)
    
    if not normalized_text.startswith('@'):
        return
    
    group_id = get_group_id_from_event(event)

    # 建立精簡化的命令上下文 (由 Service 提供資料)
    context = create_command_context(
        event=event,
        group_id=group_id,
        member_service=member_service,
        schedule_service=schedule_service,
        firebase_service=container.firebase_service,
        # 為了相容性，傳入必要回調
        reminder_callback=notification_service.send_group_reminder,
        update_schedule=lambda gid, d, h, m: schedule_service.update_schedule(gid, d, h, m, reminder_callback=notification_service.send_group_reminder)
    )
    
    response = handle_command(normalized_text, context)
    
    if response:
        messaging_api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=response)]
        ))
    else:
        # 未知指令建議
        command_part = normalized_text.split()[0]
        suggestions = suggest_commands(command_part)
        messaging_api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=ERROR_TEMPLATES['unknown_command'].format(command=command_part, suggestions=suggestions))]
        ))

@handler.add(JoinEvent)
def handle_join(event):
    """Bot 加入群組"""
    group_id = event.source.group_id
    if member_service.add_group(group_id):
        notification_service.send_welcome_message(group_id)
        print(f"➕ 加入新群組: {group_id}")
    else:
        print(f"🔄 重新加入群組: {group_id}")

@handler.add(LeaveEvent)
def handle_leave(event):
    """Bot 離開群組"""
    group_id = event.source.group_id
    if member_service.remove_group(group_id):
        print(f"➖ 離開群組: {group_id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
