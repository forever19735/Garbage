from repositories.firebase_repository import FirebaseRepository
from services.member_service import MemberService
from services.schedule_service import ScheduleService
import firebase_service

class AppContainer:
    """
    Application Container for Dependency Injection
    Holds singleton instances of services and repositories.
    """
    def __init__(self, scheduler=None, group_jobs=None):
        self.firebase_repository = FirebaseRepository()
        
        # Initialize Services
        self.member_service = MemberService(self.firebase_repository)
        self.schedule_service = None
        
        self.firebase_service = firebase_service.firebase_service_instance

        if scheduler and group_jobs is not None:
             self.init_scheduler(scheduler, group_jobs)

    def init_scheduler(self, scheduler, group_jobs):
        """Initialize services that require scheduler"""
        self.schedule_service = ScheduleService(self.firebase_repository, scheduler, group_jobs)
        # Injection ScheduleService into MemberService if needed (circular dependency resolution)
        self.member_service.schedule_service = self.schedule_service
        
        # Initialize NotificationService
        from services.notification_service import NotificationService
        self.notification_service = NotificationService(self.member_service, self.schedule_service)
