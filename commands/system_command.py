"""
系統命令處理器
處理 @status, @firebase, @backup, @reset_all, @reset_date 等指令
"""

from typing import Dict, Any, Optional, List
from commands.base_command import BaseCommand


class StatusCommand(BaseCommand):
    """查看系統狀態命令"""
    
    @property
    def name(self) -> str:
        return "@status"
    
    @property
    def aliases(self) -> List[str]:
        return ["@查看狀態", "@狀態"]
    
    @property
    def description(self) -> str:
        return "查看系統狀態"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行查看系統狀態命令"""
        get_system_status = context.get('get_system_status')
        if get_system_status:
            return get_system_status()
        else:
            return "❌ 系統狀態服務未初始化"


class FirebaseCommand(BaseCommand):
    """查看 Firebase 狀態命令"""
    
    @property
    def name(self) -> str:
        return "@firebase"
    
    @property
    def aliases(self) -> List[str]:
        return []
    
    @property
    def description(self) -> str:
        return "查看 Firebase 連接狀態"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行查看 Firebase 狀態命令"""
        firebase_service = context.get('firebase_service')
        
        if not firebase_service:
            return self._get_not_connected_message()
        
        if not firebase_service.is_available():
            return self._get_not_connected_message()
        
        try:
            firebase_stats = firebase_service.get_statistics()
            
            response = f"""🔥 Firebase 狀態報告

✅ 連接狀態: 已連接
📊 資料統計:
  └ 總文件數: {firebase_stats.get('total_documents', 0)}
  └ 集合數量: {len(firebase_stats.get('collections', {}))}

📁 集合詳情:"""
            
            for collection_name, doc_count in firebase_stats.get('collections', {}).items():
                response += f"\n  └ {collection_name}: {doc_count} 個文件"
            
            response += """

🔄 資料同步: 自動同步到 Firebase
💾 本地備份: 同時保存到本地檔案
⚡ 提示: 所有資料變更都會即時同步"""
            
            return response
            
        except Exception as e:
            return f"""🔥 Firebase 狀態報告

✅ 連接狀態: 已連接
❌ 統計錯誤: {str(e)}

💡 建議: Firebase 已連接但取得統計時發生錯誤"""
    
    def _get_not_connected_message(self) -> str:
        return """🔥 Firebase 狀態報告

❌ 連接狀態: 未連接
📝 原因: Firebase 配置未設定或初始化失敗

🔧 設定方式:
1. 設定環境變數 FIREBASE_CONFIG_JSON
2. 或放置 firebase-service-account.json 檔案
3. 或使用 Google Cloud 預設憑證

💾 目前模式: 本地檔案儲存
⚠️ 提醒: 本地檔案可能在部署時遺失"""


class BackupCommand(BaseCommand):
    """備份資料命令"""
    
    @property
    def name(self) -> str:
        return "@backup"
    
    @property
    def aliases(self) -> List[str]:
        return ["@備份"]
    
    @property
    def description(self) -> str:
        return "備份資料到 Firebase"
    
    def execute(self, event, text: str, context: Dict[str, Any]) -> Optional[str]:
        """執行備份命令"""
        firebase_service = context.get('firebase_service')
        
        if not firebase_service or not firebase_service.is_available():
            return "❌ Firebase 無法連接，備份功能暫時不可用"
        
        try:
            backup_result = firebase_service.create_backup()
            
            if backup_result:
                return """✅ 資料備份已完成！

☁️ 備份位置: Firebase Firestore
🔒 資料安全: 雲端自動保護
📊 備份內容: 群組設定、成員資料、排程設定

💡 備份優勢:
• 自動版本控制
• 即時同步
• 無需手動設定
• 企業級可靠性

⚡ 使用 @backup 指令隨時備份資料"""
            else:
                return "⚠️ Firebase 備份建立失敗，請稍後再試"
                
        except Exception as e:
            return f"❌ 備份失敗: {str(e)}"


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
        if reset_all_data:
            result = reset_all_data()
            return f"🔄 {result['message']}"
        else:
            return "❌ 重置服務未初始化"


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
status_command = StatusCommand()
firebase_command = FirebaseCommand()
backup_command = BackupCommand()
reset_all_command = ResetAllCommand()
reset_date_command = ResetDateCommand()
clear_groups_command = ClearGroupsCommand()
debug_env_command = DebugEnvCommand()
