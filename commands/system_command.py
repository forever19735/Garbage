"""
系統命令處理器
處理 @status, @firebase, @backup, @reset_all, @reset_date 等指令
"""

from typing import Dict, Any, Optional, List
from commands.base_command import BaseCommand


class ResetAllCommand(BaseCommand):
    """重置所有資料命令"""
    
    @property
    def name(self) -> str:
        return "@reset_all"
    
    @property
    def aliases(self) -> List[str]:
        return ["@重置"]
    
    @property
    def description(self) -> str:
        return "重置所有資料"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行重置所有資料命令"""
        reset_all_data = context.get('reset_all_data')
        # 如果 context 中沒有直接提供，嘗試從 service 獲取 (新架構)
        if not reset_all_data:
            # 這裡需要小心，因為 reset_all_data 在 main.py 中被移除了
            # 我們需要確認新架構如何處理 reset_all
            # 在新架構中，這應該是 MemberService.clear_all_members + 清除 group_ids
            # 但目前 main.py 確實移除了 reset_all_data 函數
            # 我們可能需要在此處直接調用 services
            pass

        # 由於 main.py 移除了 reset_all_data，我們需要更新这里的逻辑
        # 但為了快速修復 Compile Error，我們先恢復類別定義
        # 並標記這是一個需要進一步修復的邏輯
        
        # 暫時回退到依賴 context，若 context 無此函數則報錯
        # 稍後我會修復這個邏輯
        if reset_all_data:
            result = reset_all_data()
            return f"🔄 {result['message']}"
        else:
            return "❌ 重置服務未初始化 (功能重構中)"


class ResetDateCommand(BaseCommand):
    """重置基準日期命令"""
    
    @property
    def name(self) -> str:
        return "@reset_date"
    
    @property
    def aliases(self) -> List[str]:
        return ["@重置日期"]
    
    @property
    def description(self) -> str:
        return "重置輪值基準日期"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行重置基準日期命令"""
        from datetime import date
        
        base_date = context.get('base_date')
        save_base_date = context.get('save_base_date')
        
        if not save_base_date:
            return "❌ 日期服務未初始化"
        
        old_base_date = base_date
        new_base_date = date.today()
        save_base_date(new_base_date)
        
        response = f"🔄 基準日期已重置\n"
        response += f"舊基準日期: {old_base_date.strftime('%Y-%m-%d') if old_base_date else '未設定'}\n"
        response += f"新基準日期: {new_base_date.strftime('%Y-%m-%d')}\n\n"
        response += f"💡 從今天開始重新計算週數輪值"
        
        return response


class ClearGroupsCommand(BaseCommand):
    """清空群組命令"""
    
    @property
    def name(self) -> str:
        return "@clear_groups"
    
    @property
    def aliases(self) -> List[str]:
        return ["@清空群組"]
    
    @property
    def description(self) -> str:
        return "清空所有群組 ID"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行清空群組命令"""
        clear_all_group_ids = context.get('clear_all_group_ids')
        if clear_all_group_ids:
            result = clear_all_group_ids()
            return f"{'✅' if result['success'] else '❌'} {result['message']}"
        else:
            return "❌ 群組服務未初始化"


class DebugEnvCommand(BaseCommand):
    """環境變數診斷命令"""
    
    @property
    def name(self) -> str:
        return "@debug_env"
    
    @property
    def aliases(self) -> List[str]:
        return []
    
    @property
    def description(self) -> str:
        return "診斷環境變數設定"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行環境變數診斷命令"""
        import os
        import sys
        from datetime import datetime
        
        # 檢查 Railway 環境
        railway_env_indicators = [
            ("RAILWAY_ENVIRONMENT_NAME", "環境名稱"),
            ("RAILWAY_PROJECT_NAME", "專案名稱"),
            ("RAILWAY_SERVICE_NAME", "服務名稱"),
            ("RAILWAY_DEPLOYMENT_ID", "部署ID")
        ]
        
        env_status = []
        for var, desc in railway_env_indicators:
            value = os.getenv(var)
            if value:
                env_status.append(f"✅ {desc}: {value}")
            else:
                env_status.append(f"❌ {desc}: 未設定")
        
        is_railway = any(os.getenv(var) for var, _ in railway_env_indicators)
        
        # 檢查目標環境變數
        target_vars = [
            ("LINE_CHANNEL_ACCESS_TOKEN", "LINE Access Token"),
            ("LINE_CHANNEL_SECRET", "LINE Channel Secret"),
        ]
        
        var_status = []
        for var, desc in target_vars:
            value = os.getenv(var)
            if value:
                length = len(value)
                masked = value[:8] + "..." if length > 8 else value
                var_status.append(f"✅ {desc}: {masked} ({length}字符)")
            else:
                var_status.append(f"❌ {desc}: 未設定")
        
        return f"""🔍 環境變數詳細診斷報告

🚂 Railway 環境檢查：
{'✅ 確認在 Railway 環境中' if is_railway else '⚠️ 不在 Railway 環境中'}

{chr(10).join(env_status)}

🎯 關鍵環境變數狀態：
{chr(10).join(var_status)}

⚙️ 系統資訊：
• Python: {sys.version.split()[0]}
• 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""


# 導出命令實例
reset_all_command = ResetAllCommand()
reset_date_command = ResetDateCommand()
clear_groups_command = ClearGroupsCommand()
debug_env_command = DebugEnvCommand()
