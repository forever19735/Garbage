
import logging
import firebase_service

logger = logging.getLogger(__name__)

class FirebaseRepository:
    """
    Firebase 資料存儲庫
    
    負責處理所有與 Firebase 的資料交互，取代原有的 DataManager
    """
    
    def __init__(self):
        self.firebase_service = firebase_service.firebase_service_instance
    
    def is_available(self):
        """檢查 Firebase 服務是否可用"""
        return self.firebase_service.is_available()

    def load_data(self, data_type, default_value=None):
        """從 Firebase 載入資料"""
        if not self.is_available():
            print(f"⚠️ Firebase 未連接，無法載入 {data_type}")
            return default_value if default_value is not None else ([] if data_type in ['group_ids'] else {})
        
        try:
            if data_type == 'group_ids':
                firebase_data = self.firebase_service.load_group_ids()
            elif data_type == 'groups':
                firebase_data = self.firebase_service.load_groups()
            elif data_type == 'base_date':
                firebase_data = self.firebase_service.load_base_date()
            elif data_type == 'group_schedules':
                firebase_data = self.firebase_service.load_group_schedules()
            elif data_type == 'group_messages':
                # 注意：如果 firebase_service 沒有 implement 這個方法，這裡會報錯
                # 暫時保留以相容 main.py 的邏輯，建議後續在 firebase_service 補上
                if hasattr(self.firebase_service, 'load_group_messages'):
                    firebase_data = self.firebase_service.load_group_messages()
                else:
                    return default_value if default_value is not None else {}
            else:
                firebase_data = None
            
            if firebase_data is not None:
                return firebase_data
        except Exception as e:
            logger.error(f"從 Firebase 載入 {data_type} 失敗: {e}")
            print(f"⚠️ 從 Firebase 載入 {data_type} 失敗: {e}")
        
        return default_value if default_value is not None else ([] if data_type in ['group_ids'] else {})
    
    def save_data(self, data_type, data):
        """儲存資料到 Firebase"""
        if not self.is_available():
            print(f"⚠️ Firebase 未連接，無法儲存 {data_type}")
            return False
        
        try:
            if data_type == 'group_ids':
                return self.firebase_service.save_group_ids(data)
            elif data_type == 'groups':
                return self.firebase_service.save_groups(data)
            elif data_type == 'base_date':
                return self.firebase_service.save_base_date(data)
            elif data_type == 'group_schedules':
                return self.firebase_service.save_group_schedules(data)
            elif data_type == 'group_messages':
                if hasattr(self.firebase_service, 'save_group_messages'):
                    return self.firebase_service.save_group_messages(data)
                else:
                    logger.warning("firebase_service 缺少 save_group_messages 方法")
                    return False
        except Exception as e:
            logger.error(f"儲存 {data_type} 到 Firebase 失敗: {e}")
            print(f"⚠️ 儲存 {data_type} 到 Firebase 失敗: {e}")
            return False
        
        return False
    
    def delete_data(self, data_type):
        """從 Firebase 刪除資料"""
        if not self.is_available():
            print(f"⚠️ Firebase 未連接，無法刪除 {data_type}")
            return False
        
        try:
            if data_type == 'base_date':
                return self.firebase_service.reset_base_date()
        except Exception as e:
            logger.error(f"從 Firebase 刪除 {data_type} 失敗: {e}")
            print(f"⚠️ 從 Firebase 刪除 {data_type} 失敗: {e}")
            return False
        
        return False
