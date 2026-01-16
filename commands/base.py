"""Base command interface"""
from abc import ABC, abstractmethod
from typing import Optional


class Command(ABC):
    """Abstract base class for all commands"""
    
    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Check if this command can handle the given text"""
        pass
    
    @abstractmethod
    def execute(self, event) -> str:
        """Execute the command and return response message"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name for logging and debugging"""
        pass


class CommandHandler:
    """Handles command registration and execution"""
    
    def __init__(self):
        self.commands: list = []
    
    def register(self, command: Command) -> None:
        """Register a new command handler"""
        self.commands.append(command)
    
    def handle(self, event) -> Optional[str]:
        """Find and execute appropriate command"""
        if not hasattr(event.message, 'text'):
            return None
            
        text = event.message.text.strip()
        
        for command in self.commands:
            if command.can_handle(text):
                try:
                    return command.execute(event)
                except Exception as e:
                    print(f"Error executing command {command.name}: {e}")
                    return f"❌ 執行指令時發生錯誤：{str(e)}"
        
        return None  # No command matched
