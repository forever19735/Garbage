import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class FirebaseService:
    def __init__(self):
        self.db = None
        self.initialized = False
        if FIREBASE_AVAILABLE:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        try:
            if firebase_admin._apps:
                self.db = firestore.client()
                self.initialized = True
                return
            
            firebase_config = os.getenv('FIREBASE_CONFIG_JSON')
            if firebase_config:
                config_dict = json.loads(firebase_config)
                cred = credentials.Certificate(config_dict)
            else:
                service_account_path = 'firebase-service-account.json'
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                else:
                    self.initialized = False
                    return
            
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Firebase 初始化失敗: {e}")
            self.initialized = False
    
    def is_available(self):
        return FIREBASE_AVAILABLE and self.initialized and self.db is not None
    
    def load_group_ids(self):
        if not self.is_available():
            return []
        try:
            doc_ref = self.db.collection('bot_config').document('group_ids')
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data.get('group_ids', [])
            return []
        except Exception as e:
            logger.error(f"Firebase 載入群組 ID 失敗: {e}")
            return []
    
    def save_group_ids(self, group_ids):
        if not self.is_available():
            return False
        try:
            doc_ref = self.db.collection('bot_config').document('group_ids')
            data = {'group_ids': group_ids, 'updated_at': firestore.SERVER_TIMESTAMP}
            doc_ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Firebase 儲存群組 ID 失敗: {e}")
            return False
    
    def load_groups(self):
        if not self.is_available():
            return {}
        try:
            doc_ref = self.db.collection('bot_config').document('groups')
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data.get('groups', {})
            return {}
        except Exception as e:
            logger.error(f"Firebase 載入群組資料失敗: {e}")
            return {}
    
    def save_groups(self, groups):
        if not self.is_available():
            return False
        try:
            doc_ref = self.db.collection('bot_config').document('groups')
            data = {'groups': groups, 'updated_at': firestore.SERVER_TIMESTAMP}
            doc_ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Firebase 儲存群組資料失敗: {e}")
            return False
    
    def load_base_date(self):
        if not self.is_available():
            return None
        try:
            doc_ref = self.db.collection('bot_config').document('base_date')
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                base_date_str = data.get('base_date')
                if base_date_str:
                    return datetime.fromisoformat(base_date_str).date()
            return None
        except Exception as e:
            logger.error(f"Firebase 載入基準日期失敗: {e}")
            return None
    
    def save_base_date(self, base_date):
        if not self.is_available():
            return False
        try:
            doc_ref = self.db.collection('bot_config').document('base_date')
            data = {'base_date': base_date.isoformat(), 'set_at': firestore.SERVER_TIMESTAMP}
            doc_ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Firebase 儲存基準日期失敗: {e}")
            return False
    
    def reset_base_date(self):
        if not self.is_available():
            return False
        try:
            doc_ref = self.db.collection('bot_config').document('base_date')
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Firebase 刪除基準日期失敗: {e}")
            return False
    
    def load_group_schedules(self):
        if not self.is_available():
            return {}
        try:
            doc_ref = self.db.collection('bot_config').document('group_schedules')
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data.get('schedules', {})
            return {}
        except Exception as e:
            logger.error(f"Firebase 載入排程設定失敗: {e}")
            return {}
    
    def save_group_schedules(self, schedules):
        if not self.is_available():
            return False
        try:
            doc_ref = self.db.collection('bot_config').document('group_schedules')
            data = {'schedules': schedules, 'updated_at': firestore.SERVER_TIMESTAMP}
            doc_ref.set(data)
            return True
        except Exception as e:
            logger.error(f"Firebase 儲存排程設定失敗: {e}")
            return False
    
    def create_backup(self):
        if not self.is_available():
            return None
        try:
            backup_data = {
                'group_ids': self.load_group_ids(),
                'groups': self.load_groups(),
                'base_date': self.load_base_date(),
                'group_schedules': self.load_group_schedules(),
                'backup_time': datetime.now().isoformat()
            }
            if backup_data['base_date']:
                backup_data['base_date'] = backup_data['base_date'].isoformat()
            
            doc_ref = self.db.collection('backups').document(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            doc_ref.set(backup_data)
            return backup_data
        except Exception as e:
            logger.error(f"Firebase 建立備份失敗: {e}")
            return None
    
    def get_statistics(self):
        if not self.is_available():
            return {'firebase_available': False, 'error': 'Firebase 未初始化或不可用'}
        try:
            stats = {'firebase_available': True, 'collections': {}, 'total_documents': 0}
            collections = ['bot_config', 'backups']
            for collection_name in collections:
                try:
                    collection_ref = self.db.collection(collection_name)
                    docs = list(collection_ref.stream())
                    doc_count = len(docs)
                    stats['collections'][collection_name] = doc_count
                    stats['total_documents'] += doc_count
                except Exception as e:
                    stats['collections'][collection_name] = f"錯誤: {e}"
            return stats
        except Exception as e:
            return {'firebase_available': False, 'error': str(e)}
    
    def migrate_from_local_files(self, local_data):
        if not self.is_available():
            return False
        try:
            success_count = 0
            total_count = 0
            
            if 'group_ids' in local_data:
                total_count += 1
                if self.save_group_ids(local_data['group_ids']):
                    success_count += 1
            
            if 'groups' in local_data:
                total_count += 1
                if self.save_groups(local_data['groups']):
                    success_count += 1
            
            if 'base_date' in local_data and local_data['base_date']:
                total_count += 1
                base_date = local_data['base_date']
                if isinstance(base_date, str):
                    base_date = datetime.fromisoformat(base_date).date()
                if self.save_base_date(base_date):
                    success_count += 1
            
            if 'group_schedules' in local_data:
                total_count += 1
                if self.save_group_schedules(local_data['group_schedules']):
                    success_count += 1
            
            return success_count == total_count
        except Exception as e:
            logger.error(f"資料遷移失敗: {e}")
            return False

firebase_service_instance = FirebaseService()
