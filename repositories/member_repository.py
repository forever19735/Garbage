"""Member data repository"""
from typing import Dict, List, Optional
from repositories.base import Repository


class MemberRepository:
    """Handles member data persistence"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: DataManager instance for data access
        """
        self.data_manager = data_manager
    
    def save_group(self, group_id: str, members: Dict[str, List[str]]) -> bool:
        """Save member group data"""
        all_groups = self.load_all_groups()
        all_groups[group_id] = members
        return self.data_manager.save_data('groups', all_groups)
    
    def load_group(self, group_id: str) -> Optional[Dict[str, List[str]]]:
        """Load member group data"""
        all_groups = self.load_all_groups()
        return all_groups.get(group_id)
    
    def load_all_groups(self) -> Dict[str, Dict[str, List[str]]]:
        """Load all member groups"""
        return self.data_manager.load_data('groups', {})
    
    def save_week(self, group_id: str, week_num: int, members: List[str]) -> bool:
        """Save members for a specific week"""
        group_data = self.load_group(group_id) or {}
        group_data[str(week_num)] = members
        return self.save_group(group_id, group_data)
    
    def load_week(self, group_id: str, week_num: int) -> Optional[List[str]]:
        """Load members for a specific week"""
        group_data = self.load_group(group_id)
        if group_data:
            return group_data.get(str(week_num))
        return None
    
    def delete_week(self, group_id: str, week_num: int) -> bool:
        """Delete members for a specific week"""
        group_data = self.load_group(group_id)
        if group_data and str(week_num) in group_data:
            del group_data[str(week_num)]
            return self.save_group(group_id, group_data)
        return False
    
    def add_member_to_week(self, group_id: str, week_num: int, member: str) -> bool:
        """Add a member to a specific week"""
        members = self.load_week(group_id, week_num) or []
        if member not in members:
            members.append(member)
            return self.save_week(group_id, week_num, members)
        return False
    
    def remove_member_from_week(self, group_id: str, week_num: int, member: str) -> bool:
        """Remove a member from a specific week"""
        members = self.load_week(group_id, week_num)
        if members and member in members:
            members.remove(member)
            return self.save_week(group_id, week_num, members)
        return False
