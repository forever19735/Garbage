"""
訊息處理器
新版的訊息處理邏輯，使用 Command Pattern
"""

from typing import Optional
from commands.handler import handle_command, create_command_context, is_known_command
from config import COMMAND_ALIASES, AVAILABLE_COMMANDS, ERROR_TEMPLATES, get_command_description


def normalize_command(text: str) -> str:
    """
    標準化指令：將中文別名轉換為英文指令
    """
    text = text.strip()
    
    for alias, target in COMMAND_ALIASES.items():
        if text.startswith(alias):
            return target + text[len(alias):]
    
    return text


def suggest_commands(input_command: str, max_suggestions: int = 3) -> str:
    """
    根據輸入的錯誤指令，建議相似的正確指令
    """
    from difflib import SequenceMatcher
    from commands import command_registry
    
    available_commands = [cmd.name for cmd in command_registry.get_all_commands()]
    
    similarities = []
    for cmd in available_commands:
        ratio = SequenceMatcher(None, input_command.lower(), cmd.lower()).ratio()
        similarities.append((cmd, ratio))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_suggestions = similarities[:max_suggestions]
    
    if not top_suggestions or top_suggestions[0][1] < 0.2:
        return "💡 試試看：@help 查看所有可用指令"
    
    suggestions = "💡 您是不是要輸入：\n"
    for cmd, ratio in top_suggestions:
        if ratio > 0.2:
            suggestions += f"  • {cmd}\n"
    
    return suggestions.rstrip()


class MessageHandler:
    """
    新版訊息處理器
    
    使用 Command Pattern 處理所有指令
    """
    
    def __init__(
        self,
        messaging_api,
        # 服務
        member_service=None,
        schedule_service=None,
        firebase_service_instance=None,
        # 資料存取
        get_groups=None,
        get_group_schedules=None,
        get_group_messages=None,
        get_base_date=None,
        # 回調函數
        reminder_callback=None,
        get_system_status=None,
        reset_all_data=None,
        save_base_date=None,
        save_group_messages=None,
        clear_all_group_ids=None,
    ):
        self.messaging_api = messaging_api
        self.member_service = member_service
        self.schedule_service = schedule_service
        self.firebase_service = firebase_service_instance
        
        # 資料存取函數
        self._get_groups = get_groups or (lambda: {})
        self._get_group_schedules = get_group_schedules or (lambda: {})
        self._get_group_messages = get_group_messages or (lambda: {})
        self._get_base_date = get_base_date or (lambda: None)
        
        # 回調函數
        self.reminder_callback = reminder_callback
        self.get_system_status = get_system_status
        self.reset_all_data = reset_all_data
        self.save_base_date = save_base_date
        self.save_group_messages = save_group_messages
        self.clear_all_group_ids = clear_all_group_ids
    
    def get_group_id_from_event(self, event) -> Optional[str]:
        """從 LINE event 物件中提取群組 ID"""
        try:
            if hasattr(event.source, 'group_id'):
                return event.source.group_id
            return None
        except Exception as e:
            print(f"取得群組 ID 失敗: {e}")
            return None
    
    def handle(self, event) -> Optional[str]:
        """
        處理訊息事件
        
        Args:
            event: LINE MessageEvent 物件
            
        Returns:
            Optional[str]: 回覆訊息
        """
        if not hasattr(event.message, 'text'):
            return None
        
        # 標準化指令
        original_text = event.message.text.strip()
        text = normalize_command(original_text)
        
        # 非命令訊息
        if not text.startswith('@'):
            return None
        
        # 取得群組 ID
        group_id = self.get_group_id_from_event(event)
        
        # 建立命令上下文
        context = create_command_context(
            event=event,
            group_id=group_id,
            # 服務
            member_service=self.member_service,
            schedule_service=self.schedule_service,
            firebase_service=self.firebase_service,
            # 資料
            groups=self._get_groups(),
            group_schedules=self._get_group_schedules(),
            group_messages=self._get_group_messages(),
            base_date=self._get_base_date(),
            # 回調函數
            reminder_callback=self.reminder_callback,
            get_system_status=self.get_system_status,
            reset_all_data=self.reset_all_data,
            save_base_date=self.save_base_date,
            save_group_messages=self.save_group_messages,
            clear_all_group_ids=self.clear_all_group_ids,
        )
        
        # 嘗試使用新的命令處理器
        response = handle_command(text, context)
        
        if response is not None:
            return response
        
        # 未知命令處理
        if text.startswith('@'):
            command_part = text.split()[0]
            suggestions = suggest_commands(command_part)
            return f"❓ 找不到指令「{command_part}」\n\n{suggestions}\n💡 輸入 @help 查看所有指令"
        
        return None
    
    def reply(self, event, message: str):
        """發送回覆訊息"""
        from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
        
        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=message)]
        )
        self.messaging_api.reply_message(req)
