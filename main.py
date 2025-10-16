from flask import Flask, request, abort
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import os

app = Flask(__name__)

# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("dQGjRjI4x4x/0aJeoO+DAivjcV0zinQbClxGETsirdIRfkGP7BYDLGOedKLQ3e1rZqgwpM1NstjrZEMQWbDTE/g+sNeqPu6xIMDNvU8dGfZHpb9vDant1973WVX7Lr8qdbA5m7JBE9xx9aCMOk+LkgdB04t89/1O/w1cDnyilFU=")
LINE_CHANNEL_SECRET = os.getenv("286b219a9f0725d1ede64665376d9600")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===== 成員輪值設定 =====
groups = [
    ["A", "B"],  # 第一週：A、B
    ["C", "D"],  # 第二週：C、D
]

# 請填入你的群組 ID（可在 Bot 加入群組後用 debug 方式取得）
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
            line_bot_api.push_message(gid, TextSendMessage(text=message))
    print(message)

# ===== 啟動排程（每週一、四 9:00）=====
scheduler = BackgroundScheduler()
scheduler.add_job(send_trash_reminder, "cron", day_of_week="mon,thu", hour=8, minute=0)
scheduler.start()

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

