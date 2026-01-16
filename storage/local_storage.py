"""Local file storage implementation (for testing/backup)"""
import json
import os
from typing import Any, Optional
from storage.base import Storage
from datetime import date


class LocalFileStorage(Storage):
    """Local JSON file storage implementation"""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize local file storage
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for a key"""
        return os.path.join(self.data_dir, f"{key}.json")
    
    def save(self, key: str, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            file_path = self._get_file_path(key)
            
            # Convert date objects to strings
            if key == 'base_date' and isinstance(data, date):
                data = data.isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已儲存 {key} 到本地檔案")
            return True
        except Exception as e:
            print(f"⚠️ 儲存 {key} 到本地檔案失敗: {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """Load data from JSON file"""
        try:
            file_path = self._get_file_path(key)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string back to date for base_date
            if key == 'base_date' and isinstance(data, str):
                from datetime import datetime
                data = datetime.fromisoformat(data).date()
            
            print(f"✅ 已從本地檔案載入 {key}")
            return data
        except Exception as e:
            print(f"⚠️ 從本地檔案載入 {key} 失敗: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete data file"""
        try:
            file_path = self._get_file_path(key)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ 已刪除本地檔案 {key}")
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ 刪除本地檔案 {key} 失敗: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if local storage is available"""
        return os.path.exists(self.data_dir) and os.access(self.data_dir, os.W_OK)
