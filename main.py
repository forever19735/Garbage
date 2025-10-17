from flask import Flask, request, abort
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.webhook import WebhookHandler, MessageEvent
from linebot.v3.messaging.models import PushMessageRequest, TextMessage
from linebot.v3.messaging.models import PushMessageRequest, TextMessage
import os

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

# ===== LINE Bot 設定 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
# 你的群組 ID，從 @debug 指令得到後再放入環境變數
# 暫時寫死測試（記得改回環境變數）
group_ids = [os.getenv("LINE_GROUP_ID") or "你的實際群組ID"]


print("ACCESS_TOKEN:", LINE_CHANNEL_ACCESS_TOKEN)
print("CHANNEL_SECRET:", LINE_CHANNEL_SECRET)
# 確認 group ids 有沒有設定
print("GROUP_ID:", group_ids)
print("RAW LINE_GROUP_ID:", repr(os.getenv("LINE_GROUP_ID")))
print("所有環境變數:")
for key, value in os.environ.items():
    if 'LINE' in key.upper():
        print(f"  {key}: {repr(value)}")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(configuration)
messaging_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===== 成員輪值設定 =====
groups = [
    ["hsinwei💐", "林志鴻"],  # 第一週
    ["徐意淳", "D"],  # 第二週
]


# ===== 判斷當週誰要收垃圾 =====
def get_current_group():
    today = date.today()
    week_num = today.isocalendar()[1]  # 第幾週
    return groups[(week_num - 1) % len(groups)]

def send_trash_reminder():
    today = date.today()
    weekday = today.weekday()  # 0=週一, 1=週二, ..., 6=週日
    weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
    print(f"DEBUG: 今天是 {today.strftime('%m/%d')}, {weekday_names[weekday]} (weekday={weekday})")
    
    # 移除週一四限制，根據排程執行
    group = get_current_group()
    
    # 根據星期決定誰收垃圾（可自訂規則）
    # 週一=0, 週二=1, 週三=2, 週四=3, 週五=4, 週六=5, 週日=6
    if weekday in [0, 3]:  # 週一、週四 -> 第一個人
        person = group[0]
    elif weekday in [1, 4]:  # 週二、週五 -> 第二個人  
        person = group[1]
    else:  # 其他天數可自訂規則
        person = group[weekday % len(group)]  # 輪流
    
    message = f"🗑️ 今天 {today.strftime('%m/%d')} ({weekday_names[weekday]}) 輪到 {person} 收垃圾！"
    
    print(f"DEBUG: 準備推播訊息: {message}")
    print(f"DEBUG: 群組 IDs: {group_ids}")

    for gid in group_ids:
        # 驗證群組 ID 格式
        if gid and gid != "你的實際群組ID" and gid.startswith("C") and len(gid) > 10:
            print(f"DEBUG: 推播到群組 {gid}")
            try:
                req = PushMessageRequest(
                    to=gid,
                    messages=[TextMessage(text=message)]
                )
                response = messaging_api.push_message(req)
                print(f"DEBUG: 推播成功 - Response: {response}")
            except Exception as e:
                print(f"DEBUG: 推播失敗 - {type(e).__name__}: {e}")
                import traceback
                print(f"DEBUG: 完整錯誤: {traceback.format_exc()}")
        else:
            if not gid or gid == "你的實際群組ID":
                print("DEBUG: 群組 ID 未設定或使用預設值，無法推播")
                print("DEBUG: 請在群組中輸入 @debug 指令來取得真實的群組 ID")
            else:
                print(f"DEBUG: 群組 ID 格式無效: {gid}")
                print("DEBUG: LINE 群組 ID 應該以 'C' 開頭，例如: C1234567890abcdef...")
    print(message)

# ===== 啟動排程（每週一、四上午 9:00）=====
from apscheduler.triggers.cron import CronTrigger
import pytz
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
job = scheduler.add_job(send_trash_reminder, "cron", day_of_week="mon,thu", hour=17, minute=10)
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
            job.remove()
            job = scheduler.add_job(send_trash_reminder, CronTrigger(day_of_week=days, hour=hour, minute=minute))
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"推播時間已更新為 {days} {hour:02d}:{minute:02d}")]
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
            hour = job.trigger.fields[1].expressions[0].value if hasattr(job, 'trigger') else 17
            minute = job.trigger.fields[0].expressions[0].value if hasattr(job, 'trigger') else 10
            job.remove()
            job = scheduler.add_job(send_trash_reminder, CronTrigger(day_of_week=days, hour=hour, minute=minute))
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"推播星期已更新為 {days}")]
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
        
        # 測試推播功能
        if event.message.text.strip() == "@test":
            print("DEBUG: 收到 @test 指令，立即執行推播測試")
            send_trash_reminder()
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="已執行推播測試，請查看 log")]
            )
            messaging_api.reply_message(req)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
