"""Time command handler - @time"""
from commands.base import Command
from utils.parsers import parse_time_flexible
from utils.formatters import format_success_message


class TimeCommand(Command):
    """Handles @time and @設定時間 commands"""
    
    def __init__(self, update_schedule_func, get_group_id_func, group_schedules):
        self.update_schedule = update_schedule_func
        self.get_group_id = get_group_id_func
        self.group_schedules = group_schedules
    
    @property
    def name(self) -> str:
        return "time"
    
    def can_handle(self, text: str) -> bool:
        return text.startswith("@time") or text.startswith("@設定時間")
    
    def execute(self, event) -> str:
        parts = event.message.text.strip().split(maxsplit=1)
        
        if len(parts) < 2:
            return "❌ 缺少時間參數\n✅ 正確格式：@time 18:30\n💡 範例：@time 09:00 或 @time 17:30"
        
        time_str = parts[1]
        hour, minute, error_msg = parse_time_flexible(time_str)
        
        if error_msg:
            return error_msg
        
        group_id = self.get_group_id(event)
        if not group_id:
            return "❌ 無法取得群組資訊\n💡 請在群組中使用此指令"
        
        result = self.update_schedule(group_id, hour=hour, minute=minute)
        
        if result["success"]:
            schedule_config = self.group_schedules.get(group_id, {})
            days = schedule_config.get("days", "mon,thu")
            
            day_mapping = {
                "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
                "fri": "週五", "sat": "週六", "sun": "週日"
            }
            day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
            days_chinese = "、".join(day_list)
            
            return format_success_message(
                "推播時間設定成功",
                {
                    "時間": f"{hour:02d}:{minute:02d} (台北時間)",
                    "星期": days_chinese,
                    "下次推播": result['schedule']['next_run']
                },
                [
                    "設定輪值成員：@week 1 姓名1,姓名2",
                    "修改推播星期：@day mon,thu",
                    "查看完整設定：@schedule"
                ]
            )
        else:
            return f"❌ 設定失敗: {result['message']}"
