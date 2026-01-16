"""
成員命令處理器
處理 @members, @week, @addmember, @removemember 指令
"""

from typing import Dict, Any, Optional, List
import re
from commands.base_command import BaseCommand


class MembersCommand(BaseCommand):
    """
    查看成員命令
    顯示成員輪值表
    """
    
    @property
    def name(self) -> str:
        return "@members"
    
    @property
    def aliases(self) -> List[str]:
        return ["@查看成員", "@成員"]
    
    @property
    def description(self) -> str:
        return "查看成員輪值表"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行查看成員命令"""
        group_id = context.get('group_id')
        
        member_service = context.get('member_service')
        if member_service:
            return member_service.get_member_schedule_summary(group_id)
        else:
            get_member_schedule_summary = context.get('get_member_schedule_summary')
            if get_member_schedule_summary:
                return get_member_schedule_summary(group_id)
            else:
                return "❌ 成員服務未初始化"


class WeekCommand(BaseCommand):
    """
    設定週成員命令
    設定指定週的輪值成員
    """
    
    @property
    def name(self) -> str:
        return "@week"
    
    @property
    def aliases(self) -> List[str]:
        return ["@設定成員"]
    
    @property
    def description(self) -> str:
        return "設定指定週的輪值成員"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行設定週成員命令"""
        parts = text.split(maxsplit=2)
        
        if len(parts) < 3:
            return self._get_format_error(text)
        
        try:
            week_num = int(parts[1])
        except ValueError:
            return self._get_format_error(text)
        
        members_str = parts[2]
        members = self._parse_members_flexible(members_str)
        
        if not members:
            return "❌ 成員列表不能為空\n✅ 正確範例：@week 1 Alice,Bob\n💡 支援分隔符：逗號、空格、頓號"
        
        group_id = context.get('group_id')
        group_schedules = context.get('group_schedules', {})
        
        member_service = context.get('member_service')
        if member_service:
            result = member_service.update_member_schedule(week_num, members, group_id)
        else:
            update_member_schedule = context.get('update_member_schedule')
            if update_member_schedule:
                result = update_member_schedule(week_num, members, group_id)
            else:
                return "❌ 成員服務未初始化"
        
        if result['success']:
            has_schedule = bool(group_schedules.get(group_id, {})) if group_id else False
            
            next_steps = []
            if not has_schedule:
                next_steps.append("設定推播時間：@cron mon,thu 18:30")
            next_steps.extend([
                "查看輪值表：@members",
                "查看排程：@schedule"
            ])
            
            return self._format_success_message(
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
    
    def _get_format_error(self, input_text: str) -> str:
        return f"""❌ 格式錯誤

📝 正確格式：@week [週數] [成員列表]
💡 範例：@week 1 Alice,Bob,Charlie

📋 說明：
• 週數：1, 2, 3... 
• 成員用逗號分隔
• 支援多種分隔符（逗號、空格、頓號）"""
    
    def _parse_members_flexible(self, members_str: str) -> List[str]:
        """彈性解析成員列表"""
        # 支援多種分隔符：逗號、頓號、空格
        members_str = members_str.replace('、', ',').replace('，', ',')
        
        # 先用逗號分隔
        if ',' in members_str:
            members = [m.strip() for m in members_str.split(',')]
        else:
            # 否則用空格分隔
            members = members_str.split()
        
        # 過濾空白成員
        return [m for m in members if m]
    
    def _format_success_message(self, action: str, details: dict, next_steps: list = None) -> str:
        message = f"✅ {action}\n\n📋 設定內容：\n"
        for key, value in details.items():
            message += f"  • {key}: {value}\n"
        if next_steps:
            message += "\n💡 下一步：\n"
            for step in next_steps:
                message += f"  • {step}\n"
        return message.rstrip()


class AddMemberCommand(BaseCommand):
    """
    添加成員命令
    添加成員到指定週
    """
    
    @property
    def name(self) -> str:
        return "@addmember"
    
    @property
    def aliases(self) -> List[str]:
        return ["@添加成員"]
    
    @property
    def description(self) -> str:
        return "添加成員到指定週"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行添加成員命令"""
        match = re.match(r"@addmember (\d+) (.+)", text.strip())
        
        if not match:
            return "格式錯誤，請輸入 @addmember 週數 成員名\n例如: @addmember 1 Alice"
        
        week_num = int(match.group(1))
        member_name = match.group(2).strip()
        group_id = context.get('group_id')
        
        member_service = context.get('member_service')
        if member_service:
            result = member_service.add_member_to_week(week_num, member_name, group_id)
        else:
            add_member_to_week = context.get('add_member_to_week')
            if add_member_to_week:
                result = add_member_to_week(week_num, member_name)
            else:
                return "❌ 成員服務未初始化"
        
        return f"{'✅' if result['success'] else '❌'} {result['message']}"


class RemoveMemberCommand(BaseCommand):
    """
    移除成員命令
    從指定週移除成員
    """
    
    @property
    def name(self) -> str:
        return "@removemember"
    
    @property
    def aliases(self) -> List[str]:
        return ["@移除成員"]
    
    @property
    def description(self) -> str:
        return "從指定週移除成員"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行移除成員命令"""
        match = re.match(r"@removemember (\d+) (.+)", text.strip())
        
        if not match:
            return "格式錯誤，請輸入 @removemember 週數 成員名\n例如: @removemember 1 Alice"
        
        week_num = int(match.group(1))
        member_name = match.group(2).strip()
        group_id = context.get('group_id')
        
        member_service = context.get('member_service')
        if member_service:
            result = member_service.remove_member_from_week(week_num, member_name, group_id)
        else:
            remove_member_from_week = context.get('remove_member_from_week')
            if remove_member_from_week:
                result = remove_member_from_week(week_num, member_name)
            else:
                return "❌ 成員服務未初始化"
        
        return f"{'✅' if result['success'] else '❌'} {result['message']}"


class ClearWeekCommand(BaseCommand):
    """
    清空週成員命令
    清空指定週的成員
    """
    
    @property
    def name(self) -> str:
        return "@clear_week"
    
    @property
    def aliases(self) -> List[str]:
        return ["@清空週"]
    
    @property
    def description(self) -> str:
        return "清空指定週的成員"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行清空週成員命令"""
        match = re.match(r"@clear_week (\d+)", text.strip())
        
        if not match:
            return "❌ 格式錯誤，請輸入 @clear_week 1 (清空第1週)"
        
        week_num = int(match.group(1))
        group_id = context.get('group_id')
        
        member_service = context.get('member_service')
        if member_service:
            result = member_service.clear_week_members(week_num, group_id)
        else:
            clear_week_members = context.get('clear_week_members')
            if clear_week_members:
                result = clear_week_members(week_num)
            else:
                return "❌ 成員服務未初始化"
        
        return f"{'✅' if result['success'] else '❌'} {result['message']}"


class ClearMembersCommand(BaseCommand):
    """
    清空所有成員命令
    """
    
    @property
    def name(self) -> str:
        return "@clear_members"
    
    @property
    def aliases(self) -> List[str]:
        return ["@清空成員"]
    
    @property
    def description(self) -> str:
        return "清空所有成員輪值安排"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行清空所有成員命令"""
        group_id = context.get('group_id')
        
        member_service = context.get('member_service')
        if member_service:
            result = member_service.clear_all_members(group_id)
        else:
            clear_all_members = context.get('clear_all_members')
            if clear_all_members:
                result = clear_all_members()
            else:
                return "❌ 成員服務未初始化"
        
        return f"{'✅' if result['success'] else '❌'} {result['message']}"


# 導出命令實例
members_command = MembersCommand()
week_command = WeekCommand()
add_member_command = AddMemberCommand()
remove_member_command = RemoveMemberCommand()
clear_week_command = ClearWeekCommand()
clear_members_command = ClearMembersCommand()
