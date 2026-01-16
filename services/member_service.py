"""
成員服務
封裝成員輪值相關的業務邏輯
"""

from datetime import date, timedelta
from typing import Dict, Any, List, Optional


class MemberService:
    """
    成員管理服務
    
    負責處理成員輪值相關的業務邏輯，包括：
    - 取得當前週的成員
    - 取得當天負責的成員
    - 更新成員安排
    - 成員輪值表摘要
    """
    
    def __init__(self, data_manager, schedule_service=None):
        """
        初始化成員服務
        
        Args:
            data_manager: DataManager 實例，用於資料存取
            schedule_service: ScheduleService 實例，用於取得排程資訊
        """
        self.data_manager = data_manager
        self.schedule_service = schedule_service
        self._groups = None
        self._base_date = None
    
    @property
    def groups(self) -> dict:
        """取得群組成員資料"""
        if self._groups is None:
            self._groups = self.data_manager.load_data('groups', {})
        return self._groups
    
    @groups.setter
    def groups(self, value: dict):
        self._groups = value
    
    @property
    def base_date(self) -> Optional[date]:
        """取得基準日期"""
        if self._base_date is None:
            self._base_date = self.data_manager.load_data('base_date', None)
        return self._base_date
    
    @base_date.setter
    def base_date(self, value: Optional[date]):
        self._base_date = value
    
    def reload_data(self):
        """重新載入資料"""
        self._groups = None
        self._base_date = None
    
    def get_current_group(self, group_id: str = None) -> List[str]:
        """
        取得當前週的成員群組（基於自然週計算）
        
        Args:
            group_id: 群組ID，如果為None則使用legacy模式
            
        Returns:
            當前週的成員列表
        """
        groups = self.groups
        base_date = self.base_date
        
        if not isinstance(groups, dict) or len(groups) == 0:
            return []
        
        # 決定使用哪個群組的資料
        if group_id is None:
            if "legacy" in groups:
                group_data = groups["legacy"]
            elif groups:
                group_data = next(iter(groups.values()))
            else:
                return []
        else:
            if group_id not in groups:
                return []
            group_data = groups[group_id]
        
        if not isinstance(group_data, dict) or len(group_data) == 0:
            return []
        
        today = date.today()
        
        # 檢查並修復 base_date
        if base_date is None or not isinstance(base_date, date):
            base_date = today
            self._save_base_date(base_date)
        
        # 計算基準日期所在自然週的星期一
        base_monday = base_date - timedelta(days=base_date.weekday())
        
        # 計算今天所在自然週的星期一
        today_monday = today - timedelta(days=today.weekday())
        
        # 計算相差多少個自然週
        weeks_diff = (today_monday - base_monday).days // 7
        
        # 計算當前是第幾週
        total_weeks = len(group_data)
        if total_weeks == 0:
            return []
        
        current_week = (weeks_diff % total_weeks) + 1
        week_key = str(current_week)
        return group_data.get(week_key, [])
    
    def get_current_day_member(self, group_id: str, target_date: date = None, group_schedules: dict = None) -> Optional[str]:
        """
        取得當前日期對應的輪值成員（支援週內按日輪值）
        
        Args:
            group_id: 群組ID
            target_date: 目標日期，如果為None則使用今天
            group_schedules: 群組排程設定
            
        Returns:
            當天負責的成員名稱，如果沒有則回傳None
        """
        if target_date is None:
            target_date = date.today()
        
        current_members = self.get_current_group(group_id)
        if not current_members:
            return None
        
        # 如果沒有排程服務或排程設定，返回第一個成員
        if group_schedules is None or group_id not in group_schedules:
            return current_members[0] if current_members else None
        
        schedule = group_schedules[group_id]
        if 'days' not in schedule:
            return current_members[0] if current_members else None
        
        # 取得推播日列表
        broadcast_days = schedule['days']
        if isinstance(broadcast_days, str):
            broadcast_days = [d.strip() for d in broadcast_days.split(',')]
        elif not isinstance(broadcast_days, list):
            return current_members[0] if current_members else None
        
        # 星期對應
        day_mapping = {
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
            'fri': 4, 'sat': 5, 'sun': 6
        }
        
        # 取得今天是星期幾
        today_weekday = target_date.weekday()
        
        # 找出今天的星期名
        today_day_name = None
        for day_name, day_num in day_mapping.items():
            if day_num == today_weekday:
                today_day_name = day_name
                break
        
        if today_day_name not in broadcast_days:
            return None  # 今天不是推播日
        
        # 根據推播日順序分配成員
        day_index = broadcast_days.index(today_day_name)
        member_index = day_index % len(current_members)
        return current_members[member_index]
    
    def get_member_schedule(self, group_id: str = None) -> Dict[str, Any]:
        """
        取得成員輪值安排資訊
        
        Args:
            group_id: 群組ID
            
        Returns:
            包含成員輪值資訊的字典
        """
        groups = self.groups
        base_date = self.base_date
        
        empty_result = {
            "total_weeks": 0,
            "current_week": 1,
            "base_date": None,
            "group_id": group_id,
            "schedule": {},
            "current_members": [],
            "weeks": []
        }
        
        if not isinstance(groups, dict):
            return empty_result
        
        # 決定使用哪個群組的資料
        if group_id is None:
            if "legacy" in groups:
                group_data = groups["legacy"]
                effective_group_id = "legacy"
            elif groups:
                effective_group_id = next(iter(groups.keys()))
                group_data = groups[effective_group_id]
            else:
                return empty_result
        else:
            if group_id not in groups:
                return empty_result
            group_data = groups[group_id]
            effective_group_id = group_id
        
        if not isinstance(group_data, dict):
            return empty_result
        
        total_weeks = len(group_data)
        today = date.today()
        
        # 計算當前週
        if base_date is not None and total_weeks > 0:
            base_monday = base_date - timedelta(days=base_date.weekday())
            today_monday = today - timedelta(days=today.weekday())
            weeks_diff = (today_monday - base_monday).days // 7
            current_week = (weeks_diff % total_weeks) + 1
            days_since_start = (today - base_monday).days
        else:
            current_week = 1
            days_since_start = 0
            weeks_diff = 0
        
        current_week_key = str(current_week)
        current_members = group_data.get(current_week_key, [])
        
        result = {
            "total_weeks": total_weeks,
            "current_week": current_week,
            "base_date": base_date.isoformat() if base_date else None,
            "group_id": effective_group_id,
            "calculation_method": "natural_week",
            "days_since_start": days_since_start,
            "weeks_diff": weeks_diff,
            "current_members": current_members,
            "weeks": []
        }
        
        # 建立週次資訊
        for week_key in sorted(group_data.keys(), key=lambda x: int(x)):
            week_num = int(week_key)
            week_members = group_data[week_key]
            result["weeks"].append({
                "week": week_num,
                "members": week_members.copy(),
                "member_count": len(week_members),
                "is_current": week_num == current_week
            })
        
        return result
    
    def update_member_schedule(self, week_num: int, members: List[str], group_id: str = None) -> Dict[str, Any]:
        """
        更新指定週的成員安排
        
        Args:
            week_num: 週數 (1-based)
            members: 成員列表
            group_id: 群組ID
            
        Returns:
            操作結果
        """
        if not isinstance(week_num, int) or week_num < 1:
            return {"success": False, "message": "週數必須是大於 0 的整數"}
        
        if not isinstance(members, list) or len(members) == 0:
            return {"success": False, "message": "成員列表不能為空"}
        
        groups = self.groups
        if not isinstance(groups, dict):
            groups = {}
        
        target_group_id = "legacy" if group_id is None else group_id
        
        if target_group_id not in groups:
            groups[target_group_id] = {}
        
        week_key = str(week_num)
        groups[target_group_id][week_key] = members.copy()
        
        # 如果沒有基準日期，設定為今天
        if self.base_date is None:
            self._save_base_date(date.today())
        
        # 儲存更新
        self.groups = groups
        self.data_manager.save_data('groups', groups)
        
        return {
            "success": True,
            "message": f"已設定第 {week_num} 週成員：{', '.join(members)}"
        }
    
    def add_member_to_week(self, week_num: int, member_name: str, group_id: str = None) -> Dict[str, Any]:
        """
        添加成員到指定週
        """
        if not isinstance(week_num, int) or week_num < 1:
            return {"success": False, "message": "週數必須是大於 0 的整數"}
        
        if not member_name or not isinstance(member_name, str):
            return {"success": False, "message": "成員名稱不能為空"}
        
        groups = self.groups
        if not isinstance(groups, dict):
            groups = {}
        
        target_group_id = "legacy" if group_id is None else group_id
        
        if target_group_id not in groups:
            groups[target_group_id] = {}
        
        week_key = str(week_num)
        if week_key not in groups[target_group_id]:
            groups[target_group_id][week_key] = []
        
        if member_name in groups[target_group_id][week_key]:
            return {"success": False, "message": f"成員 {member_name} 已在第 {week_num} 週"}
        
        groups[target_group_id][week_key].append(member_name)
        
        if self.base_date is None:
            self._save_base_date(date.today())
        
        self.groups = groups
        self.data_manager.save_data('groups', groups)
        
        return {
            "success": True,
            "message": f"成功添加 {member_name} 到第 {week_num} 週",
            "current_members": groups[target_group_id][week_key].copy()
        }
    
    def remove_member_from_week(self, week_num: int, member_name: str, group_id: str = None) -> Dict[str, Any]:
        """
        從指定週移除成員
        """
        if not isinstance(week_num, int) or week_num < 1:
            return {"success": False, "message": "週數必須是大於 0 的整數"}
        
        groups = self.groups
        if not isinstance(groups, dict):
            groups = {}
        
        target_group_id = "legacy" if group_id is None else group_id
        week_key = str(week_num)
        
        if target_group_id not in groups or week_key not in groups[target_group_id]:
            return {"success": False, "message": f"第 {week_num} 週沒有成員安排"}
        
        if member_name not in groups[target_group_id][week_key]:
            return {"success": False, "message": f"成員 {member_name} 不在第 {week_num} 週"}
        
        groups[target_group_id][week_key].remove(member_name)
        
        self.groups = groups
        self.data_manager.save_data('groups', groups)
        
        return {
            "success": True,
            "message": f"成員 {member_name} 已從第 {week_num} 週移除",
            "remaining_members": groups[target_group_id][week_key].copy()
        }
    
    def get_member_schedule_summary(self, group_id: str = None) -> str:
        """
        取得成員輪值表摘要
        """
        schedule = self.get_member_schedule(group_id)
        
        if schedule["total_weeks"] == 0:
            return "👥 尚未設定成員輪值表\n\n💡 使用「@week 1 小明,小華」來設定第1週的成員"
        
        summary = f"👥 輪值成員表\n\n"
        summary += f"📅 總共 {schedule['total_weeks']} 週輪值\n"
        summary += f"📍 目前第 {schedule['current_week']} 週\n\n"
        
        for week_info in schedule["weeks"]:
            week_num = week_info["week"]
            members = week_info["members"]
            is_current = week_info["is_current"]
            
            status = "👈 本週" if is_current else "　　　"
            member_list = "、".join(members) if members else "無成員"
            summary += f"第 {week_num} 週: {member_list} {status}\n"
        
        current_members = schedule.get("current_members", [])
        if current_members:
            summary += f"\n🗑️ 本週負責: {', '.join(current_members)}"
        else:
            summary += f"\n🗑️ 本週負責: 無成員"
        
        return summary
    
    def clear_all_members(self, group_id: str = None) -> Dict[str, Any]:
        """
        清空所有成員輪值安排
        """
        groups = self.groups
        old_count = len(groups) if isinstance(groups, dict) else 0
        
        if group_id:
            if group_id in groups:
                del groups[group_id]
        else:
            groups = {}
        
        self.groups = groups
        self.data_manager.save_data('groups', groups)
        self._save_base_date(None)
        
        return {
            "success": True,
            "message": f"已清空所有成員輪值安排 (原有 {old_count} 週資料)"
        }
    
    def clear_week_members(self, week_num: int, group_id: str = None) -> Dict[str, Any]:
        """
        清空指定週的成員安排
        """
        if not isinstance(week_num, int) or week_num < 1:
            return {"success": False, "message": "週數必須是大於 0 的整數"}
        
        groups = self.groups
        target_group_id = "legacy" if group_id is None else group_id
        week_key = str(week_num)
        
        if target_group_id not in groups or week_key not in groups[target_group_id]:
            return {"success": False, "message": f"第 {week_num} 週沒有成員安排"}
        
        old_members = groups[target_group_id][week_key].copy()
        del groups[target_group_id][week_key]
        
        self.groups = groups
        self.data_manager.save_data('groups', groups)
        
        return {
            "success": True,
            "message": f"已清空第 {week_num} 週的成員安排 (原有成員: {', '.join(old_members)})"
        }
    
    def _save_base_date(self, new_date: Optional[date]):
        """儲存基準日期"""
        self._base_date = new_date
        self.data_manager.save_data('base_date', new_date)
