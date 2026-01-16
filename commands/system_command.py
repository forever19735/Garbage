"""
系統命令處理器
處理 @status, @firebase, @backup, @reset_all, @reset_date 等指令
"""

from typing import Dict, Any, Optional, List
from commands.base_command import BaseCommand



# 導出命令實例
reset_all_command = ResetAllCommand()
reset_date_command = ResetDateCommand()
clear_groups_command = ClearGroupsCommand()
debug_env_command = DebugEnvCommand()
