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

# 動態收集的群組 ID 列表
group_ids = []

# 從環境變數載入已知的群組 ID
if os.getenv("LINE_GROUP_ID"):
    group_ids = ["C2260711e7290fc2307aebdfb60d94fd4"]


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
groups = [
    ["hsinwei💐", "林志鴻"],  # 第一週
    ["徐意淳", "D"],  # 第二週
]


# ===== 判斷當週誰要收垃圾 =====
def get_current_group():
    today = date.today()
    week_num = today.isocalendar()[1]  # 第幾週
    return groups[(week_num - 1) % len(groups)]

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
        
        # 建立新排程
        from apscheduler.triggers.cron import CronTrigger
        job = scheduler.add_job(send_trash_reminder, CronTrigger(day_of_week=days, hour=hour, minute=minute))
        
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

    if not group_ids:
        print("DEBUG: 沒有設定任何群組 ID，無法推播")
        print("DEBUG: 請在群組中輸入 @debug 指令來自動添加群組 ID")
        return

    for gid in group_ids:
        # 驗證群組 ID 格式
        if gid and gid.startswith("C") and len(gid) > 10:
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
        
        # 顯示排程摘要
        if event.message.text.strip() == "@schedule":
            summary = get_schedule_summary()
            from linebot.v3.messaging.models import ReplyMessageRequest
            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=summary)]
            )
            messaging_api.reply_message(req)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
