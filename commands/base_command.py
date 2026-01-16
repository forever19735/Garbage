"""
命令基類
所有命令處理器都應繼承此類
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseCommand(ABC):
    """
    命令基類
    
    所有命令處理器都應繼承此類並實作必要的方法。
    使用 Command Pattern 將每個指令的處理邏輯封裝在獨立的類別中。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        命令名稱
        
        Returns:
            str: 命令名稱，例如 '@schedule'
        """
        pass
    
    @property
    def aliases(self) -> List[str]:
        """
        命令別名（中文別名等）
        
        Returns:
            List[str]: 別名列表，例如 ['@排程', '@查看排程']
        """
        return []
    
    @property
    def description(self) -> str:
        """
        命令簡短描述
        
        Returns:
            str: 描述文字
        """
        return ""
    
    @abstractmethod
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """
        執行命令
        
        Args:
            event: LINE MessageEvent 物件
            text: 使用者輸入的完整文字（已標準化）
            context: 執行上下文，包含 messaging_api, group_id 等
            
        Returns:
            Optional[str]: 回覆訊息，如果為 None 則不回覆
        """
        pass
    
    def can_handle(self, text: str) -> bool:
        """
        判斷是否可以處理此訊息
        
        Args:
            text: 使用者輸入的文字
            
        Returns:
            bool: 是否可以處理
        """
        if text.startswith(self.name):
            return True
        for alias in self.aliases:
            if text.startswith(alias):
                return True
        return False
    
    def get_help(self) -> str:
        """
        取得詳細幫助訊息
        
        Returns:
            str: 幫助訊息
        """
        return f"{self.name}: {self.description}"
    
    def parse_args(self, text: str) -> List[str]:
        """
        解析命令參數
        
        Args:
            text: 完整命令文字
            
        Returns:
            List[str]: 參數列表
        """
        # 移除命令名稱，取得參數部分
        for prefix in [self.name] + self.aliases:
            if text.startswith(prefix):
                args_text = text[len(prefix):].strip()
                if args_text:
                    return args_text.split()
                return []
        return []
