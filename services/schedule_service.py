"""
排程服務
封裝推播排程相關的業務邏輯
"""

from typing import Dict, Any, Optional
from datetime import datetime


class ScheduleService:
    """
    排程管理服務
    
    負責處理推播排程相關的業務邏輯，包括：
    - 取得排程資訊
    - 更新排程設定
    - 排程摘要
    """
    
    # 星期對應表
    DAY_MAPPING = {
        "mon": "週一", "tue": "週二", "wed": "週三", "thu": "週四",
        "fri": "週五", "sat": "週六", "sun": "週日"
    }
    
    VALID_DAYS = {'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}
    
    def __init__(self, data_manager, scheduler=None, group_jobs: dict = None):
        """
        初始化排程服務
        
        Args:
            data_manager: DataManager 實例
            scheduler: APScheduler BackgroundScheduler 實例
            group_jobs: 群組排程任務字典
        """
        self.data_manager = data_manager
        self.scheduler = scheduler
        self.group_jobs = group_jobs if group_jobs is not None else {}
        self._group_schedules = None
    
    @property
    def group_schedules(self) -> dict:
        """取得群組排程設定"""
        if self._group_schedules is None:
            self._group_schedules = self.data_manager.load_data('group_schedules', {})
        return self._group_schedules
    
    @group_schedules.setter
    def group_schedules(self, value: dict):
        self._group_schedules = value
    
    def reload_data(self):
        """重新載入資料"""
        self._group_schedules = None
    
    def get_schedule_info(self, group_id: str = None) -> Dict[str, Any]:
        """
        取得排程資訊
        
        Args:
            group_id: 群組ID，如果為None則回傳所有群組的排程
            
        Returns:
            包含排程資訊的字典
        """
        if group_id:
            return self._get_group_schedule_info(group_id)
        else:
            return self._get_all_schedules_info()
    
    def _get_group_schedule_info(self, group_id: str) -> Dict[str, Any]:
        """取得特定群組的排程資訊"""
        job = self.group_jobs.get(group_id)
        
        if not job:
            return {
                "is_configured": False,
                "message": f"群組 {group_id} 排程未設定",
                "next_run_time": None,
                "schedule_details": None,
                "group_id": group_id
            }
        
        try:
            next_run = job.next_run_time
            next_run_str = next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else "未知"
            
            schedule_config = self.group_schedules.get(group_id, {})
            
            schedule_details = {
                "timezone": "Asia/Taipei",
                "days": schedule_config.get("days", "mon,thu"),
                "hour": schedule_config.get("hour", 17),
                "minute": schedule_config.get("minute", 10),
                "group_id": group_id
            }
            
            return {
                "is_configured": True,
                "message": f"群組 {group_id} 排程已設定",
                "next_run_time": next_run_str,
                "schedule_details": schedule_details,
                "group_id": group_id
            }
            
        except Exception as e:
            return {
                "is_configured": False,
                "message": f"取得群組 {group_id} 排程資訊失敗: {str(e)}",
                "next_run_time": None,
                "schedule_details": None,
                "error": str(e),
                "group_id": group_id
            }
    
    def _get_all_schedules_info(self) -> Dict[str, Any]:
        """取得所有群組的排程資訊"""
        all_schedules = {}
        for gid in self.group_schedules:
            all_schedules[gid] = self._get_group_schedule_info(gid)
        
        return {
            "is_configured": len(all_schedules) > 0,
            "message": f"目前有 {len(all_schedules)} 個群組設定排程",
            "all_groups": all_schedules
        }
    
    def update_schedule(self, group_id: str, days: str = None, hour: int = None, minute: int = None, 
                        reminder_callback=None) -> Dict[str, Any]:
        """
        更新群組推播排程設定
        
        Args:
            group_id: 群組ID
            days: 星期設定，例如 "mon,thu"
            hour: 小時 (0-23)
            minute: 分鐘 (0-59)
            reminder_callback: 發送提醒的回調函數
            
        Returns:
            操作結果
        """
        try:
            # 取得目前設定
            current_info = self.get_schedule_info(group_id)
            
            # 使用提供的參數或保持目前設定
            if days is None:
                days = current_info["schedule_details"]["days"] if current_info["is_configured"] else "mon,thu"
            if hour is None:
                hour = current_info["schedule_details"]["hour"] if current_info["is_configured"] else 17
            if minute is None:
                minute = current_info["schedule_details"]["minute"] if current_info["is_configured"] else 10
            
            # 驗證參數
            validation_result = self._validate_schedule_params(days, hour, minute)
            if not validation_result["valid"]:
                return {"success": False, "message": validation_result["message"]}
            
            # 移除舊排程
            if group_id in self.group_jobs:
                self.group_jobs[group_id].remove()
                del self.group_jobs[group_id]
            
            # 建立新排程
            if self.scheduler and reminder_callback:
                import pytz
                from apscheduler.triggers.cron import CronTrigger
                
                job = self.scheduler.add_job(
                    lambda: reminder_callback(group_id),
                    CronTrigger(
                        day_of_week=days,
                        hour=hour,
                        minute=minute,
                        timezone=pytz.timezone('Asia/Taipei')
                    )
                )
                self.group_jobs[group_id] = job
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else "未知"
            else:
                next_run = "排程器未初始化"
            
            # 儲存排程設定
            group_schedules = self.group_schedules
            group_schedules[group_id] = {
                "days": days,
                "hour": hour,
                "minute": minute
            }
            self.group_schedules = group_schedules
            self.data_manager.save_data('group_schedules', group_schedules)
            
            return {
                "success": True,
                "message": f"群組推播時間已更新為 {days} {hour:02d}:{minute:02d}",
                "schedule": {
                    "days": days,
                    "time": f"{hour:02d}:{minute:02d}",
                    "next_run": next_run,
                    "group_id": group_id
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"更新排程失敗: {str(e)}", "error": str(e)}
    
    def _validate_schedule_params(self, days: str, hour: int, minute: int) -> Dict[str, Any]:
        """驗證排程參數"""
        if not isinstance(hour, int) or not (0 <= hour <= 23):
            return {"valid": False, "message": "小時必須是 0-23 的整數"}
        
        if not isinstance(minute, int) or not (0 <= minute <= 59):
            return {"valid": False, "message": "分鐘必須是 0-59 的整數"}
        
        day_list = [d.strip() for d in days.split(',')]
        if not all(day in self.VALID_DAYS for day in day_list):
            return {"valid": False, "message": "星期格式無效，請使用 mon,tue,wed,thu,fri,sat,sun"}
        
        return {"valid": True}
    
    def get_schedule_summary(self, group_id: str = None) -> str:
        """
        取得排程摘要
        
        Args:
            group_id: 群組ID
            
        Returns:
            格式化的排程摘要字串
        """
        if group_id:
            return self._get_group_schedule_summary(group_id)
        else:
            return self._get_all_schedules_summary()
    
    def _get_group_schedule_summary(self, group_id: str) -> str:
        """取得特定群組的排程摘要"""
        info = self.get_schedule_info(group_id)
        
        if not info["is_configured"]:
            return f"❌ 群組排程未設定"
        
        details = info.get("schedule_details")
        if not details:
            return "❌ 無法取得排程詳情"
        
        # 格式化星期顯示
        days = details.get("days", "未知")
        if "," in days:
            day_list = [self.DAY_MAPPING.get(d.strip(), d.strip()) for d in days.split(",")]
            days_chinese = "、".join(day_list)
        else:
            days_chinese = self.DAY_MAPPING.get(days.strip(), days.strip())
        
        hour = details.get("hour", 0)
        minute = details.get("minute", 0)
        time_str = f"{hour:02d}:{minute:02d}"
        
        next_run = info.get("next_run_time", "未知")
        
        return f"""📅 群組垃圾輪值排程

🕐 執行時間: {time_str} (Asia/Taipei)
📆 執行星期: {days_chinese}
⏰ 下次執行: {next_run}

✅ 排程狀態: 已啟動"""
    
    def _get_all_schedules_summary(self) -> str:
        """取得所有群組的排程摘要"""
        if not self.group_schedules:
            return "❌ 尚未設定任何群組排程"
        
        summary = "📅 所有群組垃圾輪值排程\n\n"
        for gid in self.group_schedules:
            group_summary = self._get_group_schedule_summary(gid)
            summary += group_summary + "\n" + "=" * 40 + "\n"
        
        return summary.rstrip("\n=")
    
    def format_days_chinese(self, days: str) -> str:
        """將英文星期轉換為中文"""
        day_list = [self.DAY_MAPPING.get(d.strip(), d.strip()) for d in days.split(",")]
        return "、".join(day_list)
