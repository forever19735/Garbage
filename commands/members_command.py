"""Members command handler - @members"""
from commands.base import Command


class MembersCommand(Command):
    """Handles @members and @查看成員 commands"""
    
    def __init__(self, get_member_schedule_summary_func):
        self.get_member_schedule_summary = get_member_schedule_summary_func
    
    @property
    def name(self) -> str:
        return "members"
    
    def can_handle(self, text: str) -> bool:
        return text == "@members" or text == "@查看成員"
    
    def execute(self, event) -> str:
        group_id = getattr(event.source, 'group_id', None)
        return self.get_member_schedule_summary(group_id)
