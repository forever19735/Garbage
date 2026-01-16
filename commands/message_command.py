"""
訊息命令處理器
處理 @message 指令（自訂文案）
"""

from typing import Dict, Any, Optional, List
from commands.base_command import BaseCommand


class MessageCommand(BaseCommand):
    """
    自訂文案命令
    設定自訂提醒文案
    """
    
    @property
    def name(self) -> str:
        return "@message"
    
    @property
    def aliases(self) -> List[str]:
        return ["@訊息", "@文案"]
    
    @property
    def description(self) -> str:
        return "設定自訂提醒文案"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行自訂文案命令"""
        group_id = context.get('group_id')
        
        if not group_id:
            return "❌ 只能在群組中設定自訂文案"
        
        group_messages = context.get('group_messages', {})
        save_group_messages = context.get('save_group_messages')
        
        # 取得 @message 後面的內容
        if len(text) > 8:  # "@message " 長度為 9
            custom_message = text[9:].strip() if text.startswith("@message ") else text[len(self.name):].strip()
            
            if not custom_message:
                return self._get_help_message(group_id, group_messages)
            
            # 檢查是否要重置為預設
            if custom_message.lower() == "reset":
                if group_id in group_messages:
                    del group_messages[group_id]
                    if save_group_messages:
                        save_group_messages(group_messages)
                    return "✅ 已恢復為預設的垃圾收集文案！\n\n🗑️ 預設格式：\n今天 {date} ({weekday}) 輪到 {name} 收垃圾！"
                else:
                    return "💡 目前就是使用預設文案"
            
            # 設定自訂文案
            group_messages[group_id] = custom_message
            if save_group_messages:
                save_group_messages(group_messages)
            
            return f"""✅ 自訂文案設定成功！

📝 文案內容：
{custom_message}

💡 可用佔位符：
• {{name}} - 負責人姓名
• {{date}} - 日期 (MM/DD)
• {{weekday}} - 星期

範例：
📋 今天 {{date}} ({{weekday}}) 輪到 {{name}} 值日！"""
        
        else:
            return self._get_help_message(group_id, group_messages)
    
    def _get_help_message(self, group_id: str, group_messages: dict) -> str:
        """取得幫助訊息"""
        if group_id and group_id in group_messages:
            current_message = group_messages[group_id]
            return f"""📝 目前的自訂文案：
{current_message}

💡 修改文案：
@message 新的文案內容

🔄 恢復預設：
@message reset"""
        else:
            return """📝 設定自訂提醒文案

🔧 指令格式：
@message 自訂文案內容

💡 可用佔位符：
• {name} - 負責人姓名
• {date} - 日期 (MM/DD)
• {weekday} - 星期

📋 文案範例：
@message 📋 今天 {date} ({weekday}) 輪到 {name} 值日！
@message 🧹 {name}，該打掃辦公室了！({date})
@message ⚡ {weekday} 提醒：{name} 負責設備檢查

🔄 恢復預設文案：
@message reset"""


# 導出命令實例
message_command = MessageCommand()
