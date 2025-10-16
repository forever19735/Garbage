from flask import Flask, request, abort
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging.models import PushMessageRequest, TextMessage
from linebot.v3.messaging.models import PushMessageRequest, TextMessage
import os

app = Flask(__name__)

# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")


print("ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
print("CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
# 確認 group ids 有沒有設定
print("GROUP_ID:", os.getenv("LINE_GROUP_ID"))

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===== 成員輪值設定 =====
groups = [
    ["hsinwei💐", "林志鴻"],  # 第一週
    ["徐意淳", "D"],  # 第二週
]

# 你的群組 ID，從 @debug 指令得到後再放入環境變數
group_ids = [os.getenv("LINE_GROUP_ID")]

# ===== 判斷當週誰要收垃圾 =====
def get_current_group():
    today = date.today()
    week_num = today.isocalendar()[1]  # 第幾週
    return groups[(week_num - 1) % len(groups)]

def send_trash_reminder():
    today = date.today()
    weekday = today.weekday()  # 0=週一, 3=週四
    if weekday not in [0, 3]:
        return  # 只在週一、四提醒

    group = get_current_group()
    person = group[0] if weekday == 0 else group[1]
    message = f"🗑️ 今天 {today.strftime('%m/%d')} 輪到 {person} 收垃圾！"

    for gid in group_ids:
        if gid:
            req = PushMessageRequest(
                to=gid,
                messages=[TextMessage(text=message)]
            )
            messaging_api.push_message(req)
    print(message)

# ===== 啟動排程（每週一、四上午 9:00）=====
from apscheduler.triggers.cron import CronTrigger
scheduler = BackgroundScheduler()
job = scheduler.add_job(send_trash_reminder, "cron", day_of_week="mon,thu", hour=17, minute=10)
scheduler.start()

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
        # 使用者設定推播時間指令
        if event.message.text.strip().startswith("@settime"):
            import re
            m = re.match(r"@settime (\d{1,2}):(\d{2})", event.message.text.strip())
            if m:
                hour = int(m.group(1))
                minute = int(m.group(2))
                # 移除舊排程，新增新排程
                global job
                job.remove()
                job = scheduler.add_job(send_trash_reminder, CronTrigger(day_of_week="mon,thu", hour=hour, minute=minute))
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"推播時間已更新為 {hour:02d}:{minute:02d}")]
                )
                messaging_api.reply_message(req)
            else:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式錯誤，請輸入 @settime HH:MM")]
                )
                messaging_api.reply_message(req)
    if getattr(event.message, "type", None) == "text":
        print("收到訊息:", event.message.text)
        print("來源:", event.source)

        if event.message.text.strip() == "@debug":
            gid = getattr(event.source, "group_id", None)
            if gid:
                from linebot.v3.messaging.models import ReplyMessageRequest
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"群組ID是：{gid}")]
                )
                messaging_api.reply_message(req)
            else:
                req = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="這不是群組。")]
                )
                messaging_api.reply_message(req)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
