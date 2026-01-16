"""
幫助命令處理器
處理 @help 和 @quickstart 指令
"""

from typing import Dict, Any, Optional, List
from commands.base_command import BaseCommand


class HelpCommand(BaseCommand):
    """
    幫助命令
    顯示指令說明和快速入門指南
    """
    
    @property
    def name(self) -> str:
        return "@help"
    
    @property
    def aliases(self) -> List[str]:
        return ["@幫助", "@說明"]
    
    @property
    def description(self) -> str:
        return "顯示指令說明"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行幫助命令"""
        args = self.parse_args(text)
        
        if not args:
            # @help - 顯示總覽
            return self._get_overview()
        elif args[0] == "examples":
            # @help examples - 顯示範例
            return self._get_examples()
        else:
            # @help 類別 - 顯示特定類別
            category = args[0].lower()
            # 支援中文類別
            category_mapping = {
                "排程": "schedule",
                "成員": "members",
                "群組": "groups",
                "文案": "message",
                "訊息": "message"
            }
            category = category_mapping.get(category, category)
            
            if category in ["schedule", "members", "groups", "message"]:
                return self._get_category_help(category)
            else:
                return "❌ 未知類別\n\n💡 可用類別：\n• @help schedule（排程）\n• @help members（成員）\n• @help groups（群組）\n• @help message（文案）\n• @help examples（範例）"
    
    def _get_overview(self) -> str:
        """取得幫助總覽"""
        return """📖 輪值提醒 Bot 指令說明

🔧 排程設定
• @cron [星期] [時間] - 設定推播排程
• @time [時間] - 只修改推播時間
• @day [星期] - 只修改推播星期
• @schedule - 查看排程設定

👥 成員管理
• @week [週數] [成員] - 設定週輪值成員
• @addmember [週數] [成員] - 添加成員
• @removemember [週數] [成員] - 移除成員
• @members - 查看成員輪值表

📝 文案設定
• @message [文案] - 設定自訂文案
• @message reset - 恢復預設文案

🔍 系統狀態
• @status - 查看系統狀態
• @firebase - 查看 Firebase 狀態
• @backup - 備份資料

🔄 重置功能
• @reset_date - 重置基準日期
• @clear_week [週數] - 清空指定週成員
• @clear_members - 清空所有成員
• @reset_all - 重置所有資料

💡 輸入 @help [類別] 查看詳細說明
💡 輸入 @help examples 查看使用範例
💡 輸入 @quickstart 開始快速設定"""
    
    def _get_examples(self) -> str:
        """取得使用範例"""
        return """📋 指令使用範例

🚀 快速設定（3步驟）：
1️⃣ @cron mon,thu 18:30
2️⃣ @week 1 小明,小華
3️⃣ @week 2 小美,小強

⏰ 排程設定範例：
• @cron mon,wed,fri 09:00
• @time 17:30
• @day tue,thu

👥 成員設定範例：
• @week 1 Alice,Bob,Charlie
• @week 2 David,Eve
• @addmember 1 Frank
• @removemember 2 Eve

📝 文案設定範例：
• @message 今天輪到{name}值日！
• @message 📋 {date}({weekday}) {name}負責清潔
• @message reset

💡 支援中文指令：
• @設定排程 mon,thu 18:30
• @設定成員 1 小明,小華
• @幫助"""
    
    def _get_category_help(self, category: str) -> str:
        """取得特定類別的詳細幫助"""
        help_texts = {
            "schedule": """⏰ 排程設定指令

@cron [星期] [時間]
設定完整推播排程
• 星期格式：mon,tue,wed,thu,fri,sat,sun
• 時間格式：HH:MM（24小時制）
• 範例：@cron mon,thu 18:30

@time [時間]
只修改推播時間
• 範例：@time 09:00

@day [星期]
只修改推播星期
• 範例：@day mon,wed,fri

@schedule
查看目前排程設定""",

            "members": """👥 成員管理指令

@week [週數] [成員列表]
設定指定週的輪值成員
• 週數：1, 2, 3...
• 成員：用逗號分隔
• 範例：@week 1 Alice,Bob,Charlie

@addmember [週數] [成員]
添加成員到指定週
• 範例：@addmember 1 David

@removemember [週數] [成員]
從指定週移除成員
• 範例：@removemember 1 Alice

@members
查看成員輪值表""",

            "groups": """🏠 群組管理

Bot 會自動管理群組 ID：
• 加入群組時自動記錄
• 離開群組時自動移除

每個群組有獨立的：
• 推播排程設定
• 成員輪值表
• 自訂文案""",

            "message": """📝 文案設定指令

@message [文案內容]
設定自訂提醒文案

可用佔位符：
• {name} - 負責人姓名
• {date} - 日期 (MM/DD)
• {weekday} - 星期

範例：
• @message 今天輪到{name}值日！
• @message 📋 {date}({weekday}) {name}負責

@message reset
恢復預設文案"""
        }
        return help_texts.get(category, "未知類別")


class QuickstartCommand(BaseCommand):
    """
    快速開始命令
    提供互動式設定引導
    """
    
    @property
    def name(self) -> str:
        return "@quickstart"
    
    @property
    def aliases(self) -> List[str]:
        return ["@快速設定"]
    
    @property
    def description(self) -> str:
        return "開始快速設定引導"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行快速開始命令"""
        group_id = context.get('group_id')
        
        if not group_id:
            return "❌ 請在群組中使用此指令"
        
        # 從 context 取得設定狀態
        group_schedules = context.get('group_schedules', {})
        groups = context.get('groups', {})
        
        schedule_config = group_schedules.get(group_id, {})
        group_data = groups.get(group_id, {})
        
        has_schedule = bool(schedule_config)
        has_members = bool(group_data)
        
        if has_schedule and has_members:
            return self._get_completed_message(schedule_config, group_data)
        elif has_schedule:
            return self._get_need_members_message()
        elif has_members:
            return self._get_need_schedule_message()
        else:
            return self._get_initial_message()
    
    def _get_completed_message(self, schedule_config: dict, group_data: dict) -> str:
        """已完成設定的訊息"""
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
    
    def _get_need_members_message(self) -> str:
        """需要設定成員的訊息"""
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
    
    def _get_need_schedule_message(self) -> str:
        """需要設定排程的訊息"""
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
    
    def _get_initial_message(self) -> str:
        """初始設定引導訊息"""
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


# 導出命令實例
help_command = HelpCommand()
quickstart_command = QuickstartCommand()
