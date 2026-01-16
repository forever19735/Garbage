"""Member business logic service"""
from typing import Dict, List
from repositories.member_repository import MemberRepository


class MemberService:
    """Handles member-related business logic"""
    
    def __init__(self, repository: MemberRepository):
        """
        Args:
            repository: MemberRepository instance
        """
        self.repository = repository
    
    def update_week_members(self, group_id: str, week_num: int, members: List[str]) -> Dict:
        """
        Update members for a specific week
        
        Args:
            group_id: Group ID
            week_num: Week number
            members: List of member names
            
        Returns:
            dict: Result with success status and message
        """
        if not group_id:
            return {
                "success": False,
                "message": "無法取得群組資訊"
            }
        
        if week_num < 1:
            return {
                "success": False,
                "message": "週數必須大於 0"
            }
        
        if not members:
            return {
                "success": False,
                "message": "成員列表不能為空"
            }
        
        success = self.repository.save_week(group_id, week_num, members)
        
        if success:
            return {
                "success": True,
                "message": f"第 {week_num} 週成員設定成功",
                "week_num": week_num,
                "members": members
            }
        else:
            return {
                "success": False,
                "message": "儲存失敗"
            }
    
    def add_member(self, group_id: str, week_num: int, member: str) -> Dict:
        """Add a member to a specific week"""
        if not group_id:
            return {"success": False, "message": "無法取得群組資訊"}
        
        # Check if member already exists
        existing_members = self.repository.load_week(group_id, week_num) or []
        if member in existing_members:
            return {
                "success": False,
                "message": f"{member} 已經在第 {week_num} 週中"
            }
        
        success = self.repository.add_member_to_week(group_id, week_num, member)
        
        if success:
            return {
                "success": True,
                "message": f"已將 {member} 加入第 {week_num} 週"
            }
        else:
            return {
                "success": False,
                "message": "新增失敗"
            }
    
    def remove_member(self, group_id: str, week_num: int, member: str) -> Dict:
        """Remove a member from a specific week"""
        if not group_id:
            return {"success": False, "message": "無法取得群組資訊"}
        
        existing_members = self.repository.load_week(group_id, week_num) or []
        if member not in existing_members:
            return {
                "success": False,
                "message": f"{member} 不在第 {week_num} 週中"
            }
        
        success = self.repository.remove_member_from_week(group_id, week_num, member)
        
        if success:
            return {
                "success": True,
                "message": f"已將 {member} 從第 {week_num} 週移除"
            }
        else:
            return {
                "success": False,
                "message": "移除失敗"
            }
