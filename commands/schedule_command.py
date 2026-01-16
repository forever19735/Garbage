"""Schedule command handler - @schedule"""
from commands.base import Command


class ScheduleCommand(Command):
    """Handles @schedule and @查看排程 commands"""
    
    def __init__(self, get_schedule_summary_func, get_group_id_func):
        self.get_schedule_summary = get_schedule_summary_func
        self.get_group_id = get_group_id_func
    
    @property
    def name(self) -> str:
        return "schedule"
    
    def can_handle(self, text: str) -> bool:
        return text == "@schedule" or text == "@查看排程"
    
    def execute(self, event) -> str:
        group_id = self.get_group_id(event)
        
        if group_id:
            return self.get_schedule_summary(group_id)
        else:
            return "❌ 無法取得群組資訊"
