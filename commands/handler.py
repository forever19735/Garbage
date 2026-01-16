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
    # 資料
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
        # 資料
        'groups': groups or {},
        'group_schedules': group_schedules or {},
        'group_messages': group_messages or {},
        'base_date': base_date,
        # 回調函數（用於向後兼容）
        'reminder_callback': reminder_callback,
        'update_schedule': update_schedule,
        'update_member_schedule': update_member_schedule,
        'get_member_schedule_summary': get_member_schedule_summary,
        'get_schedule_summary': get_schedule_summary,
        'get_system_status': get_system_status,
        'add_member_to_week': add_member_to_week,
        'remove_member_from_week': remove_member_from_week,
        'clear_week_members': clear_week_members,
        'clear_all_members': clear_all_members,
        'clear_all_group_ids': clear_all_group_ids,
        'reset_all_data': reset_all_data,
        'save_base_date': save_base_date,
        'save_group_messages': save_group_messages,
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
