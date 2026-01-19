"""
命令處理器入口
負責初始化和執行命令
"""

from typing import Dict, Any, Optional
from commands import all_commands, command_registry


def initialize_commands():
    """初始化所有命令到註冊器"""
    command_registry.clear()
    for cmd in all_commands:
        command_registry.register(cmd)
    print(f"✅ 已註冊 {len(all_commands)} 個命令（{len(command_registry.get_command_names())} 個名稱/別名）")


def create_command_context(
    event,
    group_id: str = None,
    # 服務
    member_service=None,
    schedule_service=None,
    firebase_service=None,
    # 資料 (兼容舊代碼，但在新架構中建議直接從 Service 獲取)
    groups: dict = None,
    group_schedules: dict = None,
    group_messages: dict = None,
    base_date=None,
    # 回調函數
    reminder_callback=None,
    update_schedule=None,
    update_member_schedule=None,
    get_member_schedule_summary=None,
    get_schedule_summary=None,
    get_system_status=None,
    add_member_to_week=None,
    remove_member_from_week=None,
    clear_week_members=None,
    clear_all_members=None,
    clear_all_group_ids=None,
    reset_all_data=None,
    save_base_date=None,
    save_group_messages=None,
) -> Dict[str, Any]:
    """
    建立命令執行上下文
    
    包含命令執行所需的所有資料和服務
    """
    return {
        'event': event,
        'group_id': group_id,
        # 服務
        'member_service': member_service,
        'schedule_service': schedule_service,
        'firebase_service': firebase_service,
        # 資料 - 優先使用傳入的，否則從 Service 獲取
        'groups': groups if groups is not None else (member_service.groups if member_service else {}),
        'group_schedules': group_schedules if group_schedules is not None else (schedule_service.group_schedules if schedule_service else {}),
        'group_messages': group_messages if group_messages is not None else (member_service.group_messages if member_service else {}),
        'base_date': base_date if base_date is not None else (member_service.base_date if member_service else None),
        # 回調函數 - 優先使用傳入的，否則從 Service 獲取
        'reminder_callback': reminder_callback,
        'update_schedule': update_schedule,
        'update_member_schedule': update_member_schedule if update_member_schedule else (member_service.update_member_schedule if member_service else None),
        'get_member_schedule_summary': get_member_schedule_summary if get_member_schedule_summary else (member_service.get_member_schedule_summary if member_service else None),
        'get_schedule_summary': get_schedule_summary if get_schedule_summary else (schedule_service.get_schedule_summary if schedule_service else None),
        'get_system_status': get_system_status,
        'add_member_to_week': add_member_to_week if add_member_to_week else (member_service.add_member_to_week if member_service else None),
        'remove_member_from_week': remove_member_from_week if remove_member_from_week else (member_service.remove_member_from_week if member_service else None),
        'clear_week_members': clear_week_members if clear_week_members else (member_service.clear_week_members if member_service else None),
        'clear_all_members': clear_all_members if clear_all_members else (member_service.clear_all_members if member_service else None),
        'clear_all_group_ids': clear_all_group_ids if clear_all_group_ids else (member_service.clear_all_group_ids if member_service else None),
        'reset_all_data': reset_all_data,
        'save_base_date': save_base_date if save_base_date else (lambda d: setattr(member_service, 'base_date', d) if member_service else None),
        'save_group_messages': save_group_messages if save_group_messages else (lambda d: setattr(member_service, 'group_messages', d) if member_service else None),
    }


def handle_command(text: str, context: Dict[str, Any]) -> Optional[str]:
    """
    處理命令
    
    Args:
        text: 使用者輸入的文字（已標準化）
        context: 命令執行上下文
        
    Returns:
        Optional[str]: 回覆訊息，如果為 None 則不處理
    """
    # 查找對應的命令
    command = command_registry.get_command(text)
    
    if command is None:
        return None  # 沒有找到對應的命令
    
    try:
        # 執行命令
        event = context.get('event')
        response = command.execute(event, text, context)
        return response
    except Exception as e:
        print(f"命令執行錯誤: {command.name} - {e}")
        import traceback
        traceback.print_exc()
        return f"❌ 指令執行發生錯誤: {str(e)}"


def is_known_command(text: str) -> bool:
    """
    檢查是否為已知命令
    
    Args:
        text: 使用者輸入的文字
        
    Returns:
        bool: 是否為已知命令
    """
    if not text.startswith('@'):
        return False
    
    return command_registry.get_command(text) is not None


# 初始化命令（在模組載入時執行）
initialize_commands()
