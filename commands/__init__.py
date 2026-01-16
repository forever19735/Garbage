"""
命令模組
提供 LINE Bot 指令處理的基礎架構
"""

from commands.base_command import BaseCommand
from commands.command_registry import CommandRegistry, command_registry

# 導入所有命令
from commands.help_command import help_command, quickstart_command
from commands.schedule_command import cron_command, time_command, day_command, schedule_command
from commands.members_command import (
    members_command, week_command, add_member_command, 
    remove_member_command, clear_week_command, clear_members_command
)
from commands.system_command import (
    status_command, firebase_command, backup_command,
    reset_all_command, reset_date_command, clear_groups_command, debug_env_command
)
from commands.message_command import message_command

# 所有命令列表
all_commands = [
    # 幫助
    help_command,
    quickstart_command,
    # 排程
    cron_command,
    time_command,
    day_command,
    schedule_command,
    # 成員
    members_command,
    week_command,
    add_member_command,
    remove_member_command,
    clear_week_command,
    clear_members_command,
    # 系統
    status_command,
    firebase_command,
    backup_command,
    reset_all_command,
    reset_date_command,
    clear_groups_command,
    debug_env_command,
    # 訊息
    message_command,
]

__all__ = [
    'BaseCommand', 
    'CommandRegistry', 
    'command_registry',
    'all_commands',
]
