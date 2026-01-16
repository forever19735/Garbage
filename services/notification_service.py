"""
通知服務
負責處理 LINE Bot 的訊息推播與回覆
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime
import pytz
import os
import requests
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import PushMessageRequest, TextMessage, ReplyMessageRequest

logger = logging.getLogger(__name__)

class NotificationService:
    """
    通知服務
    
    負責處理：
    - 發送群組提醒
    - 發送歡迎訊息
    - 一般訊息推播
    """
    
    def __init__(self, member_service, schedule_service=None):
        self.member_service = member_service
        self.schedule_service = schedule_service
        self._messaging_api = None
        self._line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self._initialize_api()
        
    def _initialize_api(self):
        """初始化 LINE Messaging API"""
        if self._line_channel_access_token:
            configuration = Configuration(access_token=self._line_channel_access_token)
            api_client = ApiClient(configuration)
            self._messaging_api = MessagingApi(api_client)
        else:
            logger.warning("LINE_CHANNEL_ACCESS_TOKEN 未設定，NotificationService 無法發送訊息")
            
    def is_available(self) -> bool:
        """檢查服務是否可用"""
        return self._messaging_api is not None
        
    def send_group_reminder(self, group_id: str) -> bool:
        """
        發送特定群組的垃圾收集提醒
        
        Args:
            group_id: 群組ID
            
        Returns:
            bool: 是否發送成功
        """
        try:
            today = datetime.now(pytz.timezone('Asia/Taipei')).date()
            
            # 使用 member_service 取得負責人 (會自動 fallback 到 schedule_service)
            responsible_member = self.member_service.get_current_day_member(group_id, today)
            
            if not responsible_member:
                logger.info(f"群組 {group_id} 今天 {today} 沒有設定負責成員")
                return False
                
            # 取得群組設定的文案 (從 MemberService 載入 groups_messages 或類似結構)
            # 這裡需要注意：原本 group_messages 是在 global，現在應該移入 MemberService 或 GroupService
            # 暫時假設 MemberService 有方法可以取得，或者我們在這裡直接讀取
            # 為了保持重構順序，我們先假設 MemberService 會提供 get_group_message_template
            # 如果還沒實作，我們稍後補上
            
            # 簡單起見，我們先用預設文案，並標記需要實作的部分
            custom_message = self.member_service.get_group_message_template(group_id)
            
            weekday_names = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
            weekday = weekday_names[today.weekday()]
            date_str = f"{today.month}/{today.day}"
            
            if custom_message:
                message_text = custom_message.format(
                    name=responsible_member,
                    date=date_str,
                    weekday=weekday
                )
            else:
                message_text = f"🗑️ 今天 {date_str} ({weekday}) 輪到 {responsible_member} 收垃圾！"
                
            return self.push_message(group_id, message_text)
            
        except Exception as e:
            logger.error(f"發送群組 {group_id} 提醒失敗: {e}")
            import traceback
            traceback.print_exc()
            return False

    def send_welcome_message(self, group_id: str):
        """發送歡迎訊息"""
        welcome_msg = f"""🤖 歡迎使用輪值提醒 Bot！

🚀 快速開始：
@cron mon,thu 18:00 - 設定提醒星期和時間
@week 1 姓名1,姓名2 - 設定輪值成員
@message 今天輪到{{name}}值日！ - 自訂提醒文案（選用）
@help - 查看完整指令

💡 提示：所有設定都會自動儲存，重啟後不會遺失！"""
        return self.push_message(group_id, welcome_msg)

    def push_message(self, to: str, text: str) -> bool:
        """
        推播文字訊息
        
        Args:
            to: 目標 ID (User ID / Group ID)
            text: 訊息內容
            
        Returns:
            bool: 是否成功
        """
        if not self.is_available():
            print(f"[模擬推播] To: {to}, Text: {text}")
            return False
            
        try:
            req = PushMessageRequest(
                to=to,
                messages=[TextMessage(text=text)]
            )
            self._messaging_api.push_message(req)
            logger.info(f"推播成功 To: {to}")
            return True
        except Exception as e:
            logger.error(f"推播失敗: {e}")
            return False
            
    def reply_message(self, reply_token: str, text: str) -> bool:
        """回覆訊息"""
        if not self.is_available():
             print(f"[模擬回覆] Token: {reply_token}, Text: {text}")
             return False
             
        try:
            req = ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
            self._messaging_api.reply_message(req)
            return True
        except Exception as e:
            logger.error(f"回覆失敗: {e}")
            return False
