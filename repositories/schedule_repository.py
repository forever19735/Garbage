"""Schedule data repository"""
from typing import Dict, Optional
from repositories.base import Repository


class ScheduleRepository:
    """Handles schedule data persistence"""
    
    def __init__(self, data_manager):
        """
        Args:
            data_manager: DataManager instance for data access
        """
        self.data_manager = data_manager
    
    def save(self, group_id: str, schedule: Dict) -> bool:
        """Save schedule for a group"""
        all_schedules = self.load_all()
        all_schedules[group_id] = schedule
        return self.data_manager.save_data('group_schedules', all_schedules)
    
    def load(self, group_id: str) -> Optional[Dict]:
        """Load schedule for a group"""
        all_schedules = self.load_all()
        return all_schedules.get(group_id)
    
    def load_all(self) -> Dict[str, Dict]:
        """Load all schedules"""
        return self.data_manager.load_data('group_schedules', {})
    
    def delete(self, group_id: str) -> bool:
        """Delete schedule for a group"""
        all_schedules = self.load_all()
        if group_id in all_schedules:
            del all_schedules[group_id]
            return self.data_manager.save_data('group_schedules', all_schedules)
        return False
    
    def exists(self, group_id: str) -> bool:
        """Check if schedule exists for a group"""
        return group_id in self.load_all()
