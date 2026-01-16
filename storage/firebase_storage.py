"""Firebase storage implementation"""
from typing import Any, Optional
from storage.base import Storage
import firebase_service


class FirebaseStorage(Storage):
    """Firebase Firestore storage implementation"""
    
    def __init__(self):
        """Initialize Firebase storage"""
        self.firebase = firebase_service.firebase_service_instance
    
    def save(self, key: str, data: Any) -> bool:
        """Save data to Firestore"""
        if not self.is_available():
            print(f"⚠️ Firebase 未連接，無法儲存 {key}")
            return False
        
        try:
            # Map keys to Firebase methods
            if key == 'group_schedules':
                return self.firebase.save_group_schedules(data)
            elif key == 'groups':
                return self.firebase.save_groups(data)
            elif key == 'base_date':
                return self.firebase.save_base_date(data)
            elif key == 'group_messages':
                return self.firebase.save_group_messages(data)
            elif key == 'group_ids':
                return self.firebase.save_group_ids(data)
            else:
                print(f"⚠️ 未知的資料類型: {key}")
                return False
        except Exception as e:
            print(f"⚠️ 儲存 {key} 到 Firebase 失敗: {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """Load data from Firestore"""
        if not self.is_available():
            print(f"⚠️ Firebase 未連接，無法載入 {key}")
            return None
        
        try:
            # Map keys to Firebase methods
            if key == 'group_schedules':
                return self.firebase.load_group_schedules()
            elif key == 'groups':
                return self.firebase.load_groups()
            elif key == 'base_date':
                return self.firebase.load_base_date()
            elif key == 'group_messages':
                return self.firebase.load_group_messages()
            elif key == 'group_ids':
                return self.firebase.load_group_ids()
            else:
                print(f"⚠️ 未知的資料類型: {key}")
                return None
        except Exception as e:
            print(f"⚠️ 從 Firebase 載入 {key} 失敗: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete data from Firestore"""
        if not self.is_available():
            print(f"⚠️ Firebase 未連接，無法刪除 {key}")
            return False
        
        try:
            if key == 'base_date':
                return self.firebase.reset_base_date()
            else:
                # For other types, save empty data
                return self.save(key, {} if key != 'group_ids' else [])
        except Exception as e:
            print(f"⚠️ 從 Firebase 刪除 {key} 失敗: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Firebase is available"""
        return self.firebase.is_available()
