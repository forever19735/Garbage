"""Week command handler - @week"""
from commands.base import Command
from utils.parsers import parse_members_flexible, ERROR_TEMPLATES
from utils.formatters import format_success_message


class WeekCommand(Command):
    """Handles @week and @設定成員 commands"""
    
    def __init__(self, update_member_schedule_func, group_schedules):
        self.update_member_schedule = update_member_schedule_func
        self.group_schedules = group_schedules
    
    @property
    def name(self) -> str:
        return "week"
    
    def can_handle(self, text: str) -> bool:
        return text.startswith("@week") or text.startswith("@設定成員")
    
    def execute(self, event) -> str:
        parts = event.message.text.strip().split(maxsplit=2)
        
        if len(parts) < 3:
            return ERROR_TEMPLATES['week_format'].format(input=event.message.text.strip())
        
        try:
            week_num = int(parts[1])
        except ValueError:
            return ERROR_TEMPLATES['week_format'].format(input=event.message.text.strip())
        
        members_str = parts[2]
        members = parse_members_flexible(members_str)
        
        if not members:
            return "❌ 成員列表不能為空\n✅ 正確範例：@week 1 Alice,Bob\n💡 支援分隔符：逗號、空格、頓號"
        
        group_id = getattr(event.source, 'group_id', None)
        result = self.update_member_schedule(week_num, members, group_id)
        
        if result['success']:
            schedule_config = self.group_schedules.get(group_id, {}) if group_id else {}
            has_schedule = bool(schedule_config)
            
            next_steps = []
            if not has_schedule:
                next_steps.append("設定推播時間：@cron mon,thu 18:30")
            next_steps.extend([
                "查看輪值表：@members",
                "查看排程：@schedule"
            ])
            
            return format_success_message(
                f"第 {week_num} 週成員設定成功",
                {
                    "週數": f"第 {week_num} 週",
                    "成員": "、".join(members),
                    "成員數": f"{len(members)} 人"
                },
                next_steps
            )
        else:
            return f"❌ {result['message']}"
