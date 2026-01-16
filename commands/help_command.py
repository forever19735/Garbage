"""Help command handler - @help"""
from commands.base import Command


class HelpCommand(Command):
    """Handles @help, @幫助, @說明 commands"""
    
    def __init__(self, get_help_message_func, get_command_examples_func):
        self.get_help_message = get_help_message_func
        self.get_command_examples = get_command_examples_func
    
    @property
    def name(self) -> str:
        return "help"
    
    def can_handle(self, text: str) -> bool:
        return text.startswith("@help") or text.startswith("@幫助") or text.startswith("@說明")
    
    def execute(self, event) -> str:
        parts = event.message.text.strip().split(maxsplit=1)
        
        if len(parts) == 1:
            return self.get_help_message()
        elif parts[1] == "examples":
            return self.get_command_examples()
        else:
            category = parts[1].lower()
            category_mapping = {
                "排程": "schedule",
                "成員": "members",
                "群組": "groups",
                "文案": "message",
                "訊息": "message"
            }
            category = category_mapping.get(category, category)
            
            if category in ["schedule", "members", "groups", "message"]:
                return self.get_help_message(category)
            else:
                return "❌ 未知類別\n\n💡 可用類別：\n• @help schedule（排程）\n• @help members（成員）\n• @help groups（群組）\n• @help message（文案）\n• @help examples（範例）"
