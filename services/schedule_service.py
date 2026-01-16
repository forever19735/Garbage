"""Schedule business logic service"""
from typing import Dict, Optional
from repositories.schedule_repository import ScheduleRepository


class ScheduleService:
    """Handles schedule-related business logic"""
    
    def __init__(self, repository: ScheduleRepository, scheduler, group_jobs: dict):
        """
        Args:
            repository: ScheduleRepository instance
            scheduler: APScheduler instance
            group_jobs: Dictionary of group jobs
        """
        self.repository = repository
        self.scheduler = scheduler
        self.group_jobs = group_jobs
    
    def update_time(self, group_id: str, hour: int, minute: int) -> Dict:
        """
        Update schedule time for a group
        
        Args:
            group_id: Group ID
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            dict: Result with success status and details
        """
        # Load current schedule
        schedule = self.repository.load(group_id) or {}
        
        # Update time
        schedule['hour'] = hour
        schedule['minute'] = minute
        
        # Keep existing days or use default
        if 'days' not in schedule:
            schedule['days'] = 'mon,thu'
        
        # Save to repository
        success = self.repository.save(group_id, schedule)
        
        if success:
            # Update scheduler job
            self._update_scheduler_job(group_id, schedule)
            
            # Format next run time
            next_run = self._get_next_run_time(group_id)
            
            return {
                "success": True,
                "schedule": {
                    "hour": hour,
                    "minute": minute,
                    "days": schedule['days'],
                    "next_run": next_run
                }
            }
        else:
            return {
                "success": False,
                "message": "無法儲存排程設定"
            }
    
    def update_days(self, group_id: str, days: str) -> Dict:
        """Update schedule days for a group"""
        schedule = self.repository.load(group_id) or {}
        schedule['days'] = days
        
        # Keep existing time or use default
        if 'hour' not in schedule:
            schedule['hour'] = 17
        if 'minute' not in schedule:
            schedule['minute'] = 10
        
        success = self.repository.save(group_id, schedule)
        
        if success:
            self._update_scheduler_job(group_id, schedule)
            next_run = self._get_next_run_time(group_id)
            
            return {
                "success": True,
                "schedule": {
                    "hour": schedule['hour'],
                    "minute": schedule['minute'],
                    "days": days,
                    "next_run": next_run
                }
            }
        else:
            return {
                "success": False,
                "message": "無法儲存排程設定"
            }
    
    def update_full(self, group_id: str, days: str, hour: int, minute: int) -> Dict:
        """Update full schedule (days + time) for a group"""
        schedule = {
            'days': days,
            'hour': hour,
            'minute': minute
        }
        
        success = self.repository.save(group_id, schedule)
        
        if success:
            self._update_scheduler_job(group_id, schedule)
            next_run = self._get_next_run_time(group_id)
            
            return {
                "success": True,
                "schedule": {
                    "hour": hour,
                    "minute": minute,
                    "days": days,
                    "next_run": next_run
                }
            }
        else:
            return {
                "success": False,
                "message": "無法儲存排程設定"
            }
    
    def _update_scheduler_job(self, group_id: str, schedule: Dict):
        """Update APScheduler job (internal helper)"""
        import pytz
        from apscheduler.triggers.cron import CronTrigger
        
        # Remove old job if exists
        if group_id in self.group_jobs:
            self.group_jobs[group_id].remove()
            del self.group_jobs[group_id]
        
        # Create new job (需要 send_group_reminder 函數，這裡先占位)
        # 實際實作需要從 main.py 傳入
        pass
    
    def _get_next_run_time(self, group_id: str) -> str:
        """Get next run time for a group (internal helper)"""
        if group_id in self.group_jobs:
            next_run = self.group_jobs[group_id].next_run_time
            if next_run:
                return next_run.strftime("%Y-%m-%d (%A) %H:%M")
        return "尚未設定"
