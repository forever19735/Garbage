"""
排程命令處理器
處理 @cron, @time, @day, @schedule 指令
"""

from typing import Dict, Any, Optional, List
from commands.base_command import BaseCommand


class CronCommand(BaseCommand):
    """
    排程設定命令
    一次設定推播星期和時間
    """
    
    @property
    def name(self) -> str:
        return "@cron"
    
    @property
    def aliases(self) -> List[str]:
        return ["@設定排程"]
    
    @property
    def description(self) -> str:
        return "設定推播排程（星期和時間）"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行排程設定命令"""
        parts = text.split()
        
        if len(parts) < 3:
            return self._get_format_error(text)
        
        days = parts[1]
        time_str = parts[2]
        
        # 解析時間
        hour, minute, error_msg = self._parse_time_flexible(time_str)
        if error_msg:
            return error_msg
        
        group_id = context.get('group_id')
        if not group_id:
            return "❌ 無法取得群組資訊\n💡 請在群組中使用此指令"
        
        # 使用排程服務更新
        schedule_service = context.get('schedule_service')
        reminder_callback = context.get('reminder_callback')
        
        if schedule_service:
            result = schedule_service.update_schedule(
                group_id, days, hour, minute,
                reminder_callback=reminder_callback
            )
        else:
            # 回退到直接調用
            update_schedule = context.get('update_schedule')
            if update_schedule:
                result = update_schedule(group_id, days, hour, minute)
            else:
                return "❌ 排程服務未初始化"
        
        if result["success"]:
            days_chinese = self._format_days_chinese(days)
            return self._format_success_message(
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
    
    def _get_format_error(self, input_text: str) -> str:
        return f"""❌ 格式錯誤
        
📝 正確格式：@cron [星期] [時間]
💡 範例：@cron mon,thu 18:30

📋 星期參數說明：
• mon = 週一, tue = 週二, wed = 週三
• thu = 週四, fri = 週五, sat = 週六, sun = 週日
• 多個星期用逗號分隔：mon,wed,fri

⏰ 時間格式：HH:MM（24小時制）
• 08:00, 12:30, 18:00"""
    
    def _parse_time_flexible(self, time_str: str):
        """彈性解析時間"""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1])
            elif len(time_str) == 4:
                hour = int(time_str[:2])
                minute = int(time_str[2:])
            else:
                return None, None, f"❌ 時間格式錯誤\n✅ 正確格式：HH:MM 或 HHMM\n💡 範例：18:30 或 1830"
            
            if not (0 <= hour <= 23):
                return None, None, "❌ 小時必須在 0-23 之間"
            if not (0 <= minute <= 59):
                return None, None, "❌ 分鐘必須在 0-59 之間"
            
            return hour, minute, None
        except ValueError:
            return None, None, "❌ 時間格式錯誤，必須是數字"
    
    def _format_days_chinese(self, days: str) -> str:
        """將英文星期轉換為中文"""
        day_mapping = {
            "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
            "fri": "週五", "sat": "週六", "sun": "週日"
        }
        day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
        return "、".join(day_list)
    
    def _format_success_message(self, action: str, details: dict, next_steps: list = None) -> str:
        """格式化成功訊息"""
        message = f"✅ {action}\n\n"
        message += "📋 設定內容：\n"
        for key, value in details.items():
            message += f"  • {key}: {value}\n"
        
        if next_steps:
            message += "\n💡 下一步：\n"
            for step in next_steps:
                message += f"  • {step}\n"
        
        return message.rstrip()


class TimeCommand(BaseCommand):
    """
    時間設定命令
    只修改推播時間
    """
    
    @property
    def name(self) -> str:
        return "@time"
    
    @property
    def aliases(self) -> List[str]:
        return ["@設定時間"]
    
    @property
    def description(self) -> str:
        return "設定推播時間"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行時間設定命令"""
        parts = text.split(maxsplit=1)
        
        if len(parts) < 2:
            return "❌ 缺少時間參數\n✅ 正確格式：@time 18:30\n💡 範例：@time 09:00 或 @time 17:30"
        
        time_str = parts[1]
        hour, minute, error_msg = self._parse_time_flexible(time_str)
        
        if error_msg:
            return error_msg
        
        group_id = context.get('group_id')
        if not group_id:
            return "❌ 無法取得群組資訊\n💡 請在群組中使用此指令"
        
        schedule_service = context.get('schedule_service')
        reminder_callback = context.get('reminder_callback')
        group_schedules = context.get('group_schedules', {})
        
        if schedule_service:
            result = schedule_service.update_schedule(
                group_id, hour=hour, minute=minute,
                reminder_callback=reminder_callback
            )
        else:
            update_schedule = context.get('update_schedule')
            if update_schedule:
                result = update_schedule(group_id, hour=hour, minute=minute)
            else:
                return "❌ 排程服務未初始化"
        
        if result["success"]:
            schedule_config = group_schedules.get(group_id, {})
            days = schedule_config.get("days", "mon,thu")
            days_chinese = self._format_days_chinese(days)
            
            return self._format_success_message(
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
    
    def _parse_time_flexible(self, time_str: str):
        """彈性解析時間"""
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1])
            elif len(time_str) == 4:
                hour = int(time_str[:2])
                minute = int(time_str[2:])
            else:
                return None, None, "❌ 時間格式錯誤\n✅ 正確格式：HH:MM\n💡 範例：18:30"
            
            if not (0 <= hour <= 23):
                return None, None, "❌ 小時必須在 0-23 之間"
            if not (0 <= minute <= 59):
                return None, None, "❌ 分鐘必須在 0-59 之間"
            
            return hour, minute, None
        except ValueError:
            return None, None, "❌ 時間格式錯誤，必須是數字"
    
    def _format_days_chinese(self, days: str) -> str:
        day_mapping = {
            "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
            "fri": "週五", "sat": "週六", "sun": "週日"
        }
        day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
        return "、".join(day_list)
    
    def _format_success_message(self, action: str, details: dict, next_steps: list = None) -> str:
        message = f"✅ {action}\n\n📋 設定內容：\n"
        for key, value in details.items():
            message += f"  • {key}: {value}\n"
        if next_steps:
            message += "\n💡 下一步：\n"
            for step in next_steps:
                message += f"  • {step}\n"
        return message.rstrip()


class DayCommand(BaseCommand):
    """
    星期設定命令
    只修改推播星期
    """
    
    @property
    def name(self) -> str:
        return "@day"
    
    @property
    def aliases(self) -> List[str]:
        return ["@設定星期"]
    
    @property
    def description(self) -> str:
        return "設定推播星期"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行星期設定命令"""
        parts = text.split(maxsplit=1)
        
        if len(parts) < 2:
            return "❌ 缺少星期參數\n✅ 正確格式：@day mon,thu\n💡 範例：@day mon,wed,fri"
        
        days = parts[1]
        
        # 驗證星期格式
        valid_days = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
        day_list = [d.strip() for d in days.split(',')]
        invalid_days = [d for d in day_list if d not in valid_days]
        
        if invalid_days:
            return f"""❌ 無效的星期格式：{', '.join(invalid_days)}

✅ 有效的星期：
• mon = 週一, tue = 週二, wed = 週三
• thu = 週四, fri = 週五, sat = 週六, sun = 週日

💡 範例：@day mon,thu"""
        
        group_id = context.get('group_id')
        if not group_id:
            return "❌ 無法取得群組資訊\n💡 請在群組中使用此指令"
        
        schedule_service = context.get('schedule_service')
        reminder_callback = context.get('reminder_callback')
        group_schedules = context.get('group_schedules', {})
        
        if schedule_service:
            result = schedule_service.update_schedule(
                group_id, days=days,
                reminder_callback=reminder_callback
            )
        else:
            update_schedule = context.get('update_schedule')
            if update_schedule:
                result = update_schedule(group_id, days=days)
            else:
                return "❌ 排程服務未初始化"
        
        if result["success"]:
            schedule_config = group_schedules.get(group_id, {})
            hour = schedule_config.get("hour", 17)
            minute = schedule_config.get("minute", 10)
            days_chinese = self._format_days_chinese(days)
            
            return self._format_success_message(
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
    
    def _format_days_chinese(self, days: str) -> str:
        day_mapping = {
            "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
            "fri": "週五", "sat": "週六", "sun": "週日"
        }
        day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
        return "、".join(day_list)
    
    def _format_success_message(self, action: str, details: dict, next_steps: list = None) -> str:
        message = f"✅ {action}\n\n📋 設定內容：\n"
        for key, value in details.items():
            message += f"  • {key}: {value}\n"
        if next_steps:
            message += "\n💡 下一步：\n"
            for step in next_steps:
                message += f"  • {step}\n"
        return message.rstrip()


class ScheduleCommand(BaseCommand):
    """
    查看排程命令
    顯示目前的排程設定
    """
    
    @property
    def name(self) -> str:
        return "@schedule"
    
    @property
    def aliases(self) -> List[str]:
        return ["@查看排程", "@排程"]
    
    @property
    def description(self) -> str:
        return "查看推播排程設定"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行查看排程命令"""
        group_id = context.get('group_id')
        
        if not group_id:
            return "❌ 無法取得群組資訊"
        
        schedule_service = context.get('schedule_service')
        
        if schedule_service:
            return schedule_service.get_schedule_summary(group_id)
        else:
            get_schedule_summary = context.get('get_schedule_summary')
            if get_schedule_summary:
                return get_schedule_summary(group_id)
            else:
                return "❌ 排程服務未初始化"


# 導出命令實例
cron_command = CronCommand()
time_command = TimeCommand()
day_command = DayCommand()
schedule_command = ScheduleCommand()
