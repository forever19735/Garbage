"""Quickstart command handler - @quickstart"""
from commands.base import Command


class QuickstartCommand(Command):
    """Handles @quickstart and @快速設定 commands"""
    
    def __init__(self, get_group_id_func, group_schedules, groups):
        self.get_group_id = get_group_id_func
        self.group_schedules = group_schedules
        self.groups = groups
    
    @property
    def name(self) -> str:
        return "quickstart"
    
    def can_handle(self, text: str) -> bool:
        return text == "@quickstart" or text == "@快速設定"
    
    def execute(self, event) -> str:
        group_id = self.get_group_id(event)
        
        if not group_id:
            return "❌ 請在群組中使用此指令"
        
        schedule_config = self.group_schedules.get(group_id, {})
        group_data = self.groups.get(group_id, {})
        
        has_schedule = bool(schedule_config)
        has_members = bool(group_data)
        
        if has_schedule and has_members:
            # 已完成設定
            days = schedule_config.get("days", "")
            hour = schedule_config.get("hour", 0)
            minute = schedule_config.get("minute", 0)
            
            day_mapping = {
                "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
                "fri": "週五", "sat": "週六", "sun": "週日"
            }
            day_list = [day_mapping.get(d.strip(), d.strip()) for d in days.split(",")]
            days_chinese = "、".join(day_list)
            
            return f"""✅ 您已完成基本設定！

📋 當前設定：
⏰ 推播時間：{days_chinese} {hour:02d}:{minute:02d}
👥 輪值週數：{len(group_data)} 週

💡 您可以：
• 查看排程：@schedule
• 查看成員：@members
• 修改時間：@time 18:30
• 修改星期：@day mon,thu
• 設定文案：@message 自訂文案"""
            
        elif has_schedule:
            return """🚀 快速設定 - 步驟 2/2

✅ 推播排程已設定

📝 接下來請設定輪值成員：

方法一：直接輸入
@week 1 成員1,成員2

方法二：範例
@week 1 Alice,Bob
@week 2 Charlie,David

💡 提示：
• 支援多種分隔符（逗號、空格、頓號）
• 可設定多週輪值
• 設定完成後輸入 @members 查看"""
            
        elif has_members:
            return """🚀 快速設定 - 步驟 2/2

✅ 輪值成員已設定

📝 接下來請設定推播排程：

方法一：一次設定（推薦）
@cron mon,thu 18:30

方法二：分別設定
@time 18:30
@day mon,thu

💡 提示：
• 時間格式：18:30 或 1830
• 星期格式：mon,tue,wed,thu,fri,sat,sun
• 設定完成後輸入 @schedule 查看"""
            
        else:
            return """🚀 快速設定指南

歡迎使用輪值提醒 Bot！讓我們用 3 個步驟完成設定：

📝 步驟 1：設定推播排程
@cron mon,thu 18:30
（在週一、週四的 18:30 推播）

📝 步驟 2：設定輪值成員
@week 1 Alice,Bob
@week 2 Charlie,David
（第1週：Alice、Bob，第2週：Charlie、David）

📝 步驟 3：自訂文案（選用）
@message 今天輪到{name}值日！

💡 快速範例：
1️⃣ @cron mon,thu 18:30
2️⃣ @week 1 小明,小華
3️⃣ @week 2 小美,小強

✅ 完成後輸入 @schedule 和 @members 查看設定

🌏 支援中文指令：
@設定排程 mon,thu 18:30
@設定成員 1 小明,小華"""
