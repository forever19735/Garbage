
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_container_initialization():
    print("Testing AppContainer Initialization...")
    try:
        from container import AppContainer
        container = AppContainer()
        
        assert container.firebase_repository is not None, "FirebaseRepository not initialized"
        assert container.member_service is not None, "MemberService not initialized"
        assert container.firebase_service is not None, "FirebaseService not initialized"
        
        # ScheduleService is None initially
        assert container.schedule_service is None, "ScheduleService should be None initially"
        
        print("✅ AppContainer initialized successfully")
        return container
    except Exception as e:
        print(f"❌ AppContainer initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_services(container):
    print("\nTesting Services...")
    try:
        member_service = container.member_service
        
        # Test MemberService basic methods
        # Note: This might hit local file "db.json" or similar if Firebase not configured
        groups = member_service.groups
        print(f"✅ MemberService.groups loaded: {type(groups)}")
        
        # Init Scheduler to test ScheduleService
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        group_jobs = {}
        
        container.init_scheduler(scheduler, group_jobs)
        
        schedule_service = container.schedule_service
        assert schedule_service is not None, "ScheduleService should be initialized"
        print("✅ ScheduleService initialized")
        
        # Test interactions
        assert member_service.schedule_service == schedule_service, "MemberService should have reference to ScheduleService"
        print("✅ Dependencies correctly linked")
        
    except Exception as e:
         print(f"❌ Service testing failed: {e}")
         import traceback
         traceback.print_exc()

def test_main_import():
    print("\nTesting main.py import...")
    try:
        import main
        print("✅ main.py imported successfully")
        
        # Check if globals are set
        assert main.container is not None, "main.container should be set"
        assert main.member_service is not None, "main.member_service should be set"
        
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"Running tests in {os.getcwd()}")
    container = test_container_initialization()
    if container:
        test_services(container)
        test_main_import()
