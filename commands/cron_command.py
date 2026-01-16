"""Cron command handler - @cron"""
from commands.base import Command
from utils.parsers import parse_time_flexible, ERROR_TEMPLATES
from utils.formatters import format_success_message


class CronCommand(Command):
    """Handles @cron and @設定排程 commands"""
    
    def __init__(self, update_schedule_func, get_group_id_func):
        self.update_schedule = update_schedule_func
        self.get_group_id = get_group_id_func
    
    @property
    def name(self) -> str:
        return "cron"
    
    def can_handle(self, text: str) -> bool:
        return text.startswith("@cron") or text.startswith("@設定排程")
    
    def execute(self, event) -> str:
        parts = event.message.text.strip().split()
        
        if len(parts) < 3:
            return ERROR_TEMPLATES['cron_format'].format(input=event.message.text.strip())
        
        days = parts[1]
        time_str = parts[2]
        
        hour, minute, error_msg = parse_time_flexible(time_str)
        if error_msg:
            return error_msg
        
        group_id = self.get_group_id(event)
        if not group_id:
            return "❌ 無法取得群組資訊\n💡 請在群組中使用此指令"
        
        result = self.update_schedule(group_id, days, hour, minute)
        
        if result["success"]:
            day_mapping = {
                "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
                "fri": "週五", "sat": "週六", "sun": "週日"
            }
            day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
            days_chinese = "、".join(day_list)
            
            return format_success_message(
                "推播排程設定成功",
                {
                    "時間": f"{hour:02d}:{minute:02d} (台北時間)",
                    "星期": days_chinese,
                    "下次推播": result['schedule']['next_run']
                },
                [
                    "設定輪值成員：@week 1 姓名1,姓名2",
                    "查看完整設定：@schedule"
                ]
            )
        else:
            return f"❌ 設定失敗: {result['message']}"
