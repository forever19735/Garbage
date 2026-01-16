"""Utility functions for formatting messages"""
from typing import Dict, List, Optional


def format_success_message(action: str, details: Dict[str, str], next_steps: Optional[List[str]] = None) -> str:
    """
    格式化成功訊息，包含設定摘要和下一步建議
    
    Args:
        action: 執行的動作
        details: 設定詳情
        next_steps: 下一步建議（可選）
        
    Returns:
        str: 格式化的成功訊息
    """
    message = f"✅ {action}\n\n📋 設定摘要：\n"
    
    for key, value in details.items():
        message += f"  • {key}：{value}\n"
    
    if next_steps:
        message += "\n💡 下一步：\n"
        for step in next_steps:
            message += f"  • {step}\n"
    
    return message.strip()
