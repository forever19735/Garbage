"""Day command handler - @day"""
from commands.base import Command
from utils.parsers import ERROR_TEMPLATES
from utils.formatters import format_success_message


class DayCommand(Command):
    """Handles @day and @設定星期 commands"""
    
    def __init__(self, update_schedule_func, get_group_id_func, group_schedules):
        self.update_schedule = update_schedule_func
        self.get_group_id = get_group_id_func
        self.group_schedules = group_schedules
    
    @property
    def name(self) -> str:
        return "day"
    
    def can_handle(self, text: str) -> bool:
        return text.startswith("@day") or text.startswith("@設定星期")
    
    def execute(self, event) -> str:
        parts = event.message.text.strip().split(maxsplit=1)
        
        if len(parts) < 2:
            return "❌ 缺少星期參數\n✅ 正確格式：@day mon,thu\n💡 範例：@day mon,wed,fri"
        
        days = parts[1]
        
        # 驗證星期格式
        valid_days = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
        day_list = [d.strip() for d in days.split(',')]
        invalid_days = [d for d in day_list if d not in valid_days]
        
        if invalid_days:
            return ERROR_TEMPLATES['day_format'].format(input=days)
        
        group_id = self.get_group_id(event)
        if not group_id:
            return "❌ 無法取得群組資訊\n💡 請在群組中使用此指令"
        
        result = self.update_schedule(group_id, days=days)
        
        if result["success"]:
            day_mapping = {
                "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
                "fri": "週五", "sat": "週六", "sun": "週日"
            }
            day_list_chinese = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
            days_chinese = "、".join(day_list_chinese)
            
            schedule_config = self.group_schedules.get(group_id, {})
            hour = schedule_config.get("hour", 17)
            minute = schedule_config.get("minute", 10)
            
            return format_success_message(
                "推播星期設定成功",
                {
                    "星期": days_chinese,
                    "時間": f"{hour:02d}:{minute:02d} (台北時間)",
                    "下次推播": result['schedule']['next_run']
                },
                [
                    "設定輪值成員：@week 1 姓名1,姓名2",
                    "修改推播時間：@time 18:30",
                    "查看完整設定：@schedule"
                ]
            )
        else:
            return f"❌ 設定失敗: {result['message']}"
