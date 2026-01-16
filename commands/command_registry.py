"""
命令註冊器
管理所有命令的註冊和查找
"""

from typing import Dict, Optional, List
from commands.base_command import BaseCommand


class CommandRegistry:
    """
    命令註冊器
    
    負責管理所有命令的註冊、查找和執行。
    使用單例模式確保全局只有一個註冊器實例。
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._commands: Dict[str, BaseCommand] = {}
            self._initialized = True
    
    def register(self, command: BaseCommand) -> None:
        """
        註冊命令
        
        Args:
            command: 命令實例
        """
        # 註冊主命令名稱
        self._commands[command.name] = command
        
        # 註冊所有別名
        for alias in command.aliases:
            self._commands[alias] = command
    
    def register_all(self, commands: List[BaseCommand]) -> None:
        """
        批量註冊命令
        
        Args:
            commands: 命令實例列表
        """
        for command in commands:
            self.register(command)
    
    def get_command(self, text: str) -> Optional[BaseCommand]:
        """
        根據輸入文字查找對應的命令
        
        Args:
            text: 使用者輸入的文字
            
        Returns:
            Optional[BaseCommand]: 找到的命令，如果沒有則返回 None
        """
        # 先檢查完全匹配
        for name, command in self._commands.items():
            if text.startswith(name):
                # 確保是完整的命令（後面是空格或結束）
                remaining = text[len(name):]
                if remaining == "" or remaining.startswith(" "):
                    return command
        return None
    
    def get_all_commands(self) -> List[BaseCommand]:
        """
        取得所有已註冊的命令（去重）
        
        Returns:
            List[BaseCommand]: 命令列表
        """
        # 使用 id 去重，因為同一個命令可能有多個別名
        seen = set()
        unique_commands = []
        for command in self._commands.values():
            if id(command) not in seen:
                seen.add(id(command))
                unique_commands.append(command)
        return unique_commands
    
    def get_command_names(self) -> List[str]:
        """
        取得所有已註冊的命令名稱
        
        Returns:
            List[str]: 命令名稱列表
        """
        return list(self._commands.keys())
    
    def clear(self) -> None:
        """清除所有已註冊的命令"""
        self._commands.clear()


# 創建全域註冊器實例
command_registry = CommandRegistry()
