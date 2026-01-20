---
name: firebase-integration
description: Integrate Google Firebase Firestore for cloud data storage, implement CRUD operations, and manage data persistence
---

## When to use this skill

Use this skill when you need to:
- Set up Firebase Firestore for cloud data storage
- Implement data persistence and retrieval
- Migrate from local file storage to cloud
- Design Firestore collections and document schemas
- Handle Firebase authentication and security rules
- Create backup and restore functionality
- Monitor Firebase usage and statistics

## How to use it

### Core Components

#### 1. Firebase Service Class
Create a centralized service class for all Firebase operations:

```python
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

class FirebaseService:
    def __init__(self):
        self.db = None
        self.initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        try:
            # Load from environment variable (JSON string)
            firebase_config = os.getenv('FIREBASE_CONFIG_JSON')
            if firebase_config:
                config_dict = json.loads(firebase_config)
                cred = credentials.Certificate(config_dict)
            else:
                # Load from file
                cred = credentials.Certificate('firebase-service-account.json')
            
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.initialized = True
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            self.initialized = False
    
    def is_available(self):
        return self.initialized and self.db is not None
```

#### 2. Environment Configuration
Required environment variable:
- `FIREBASE_CONFIG_JSON` - Complete service account JSON as string

Example Railway/Heroku config:
```bash
FIREBASE_CONFIG_JSON={"type": "service_account", "project_id": "your-project", ...}
```

#### 3. Data Operations Pattern

**Save Data:**
```python
def save_data(self, collection, document, data):
    if not self.is_available():
        return False
    try:
        doc_ref = self.db.collection(collection).document(document)
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref.set(data)
        return True
    except Exception as e:
        print(f"Save failed: {e}")
        return False
```

**Load Data:**
```python
def load_data(self, collection, document):
    if not self.is_available():
        return None
    try:
        doc_ref = self.db.collection(collection).document(document)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Load failed: {e}")
        return None
```

**Delete Data:**
```python
def delete_data(self, collection, document):
    if not self.is_available():
        return False
    try:
        doc_ref = self.db.collection(collection).document(document)
        doc_ref.delete()
        return True
    except Exception as e:
        print(f"Delete failed: {e}")
        return False
```

### Data Modeling

#### Collection Structure for LINE Bot
```
bot_config/
  ├── group_ids (document)
  │   └── { group_ids: [...], updated_at: timestamp }
  ├── groups (document)
  │   └── { groups: {group_id: {...}}, updated_at: timestamp }
  ├── base_date (document)
  │   └── { base_date: "YYYY-MM-DD", set_at: timestamp }
  └── group_schedules (document)
      └── { schedules: {group_id: {...}}, updated_at: timestamp }

backups/
  └── backup_YYYYMMDD_HHMMSS (document)
      └── { all snapshot data }
```

### Best Practices

1. **Error Handling**
   - Always check `is_available()` before operations
   - Wrap Firebase calls in try-except blocks
   - Return sensible defaults on failure
   - Log errors for debugging

2. **Data Validation**
   - Validate data before saving to Firestore
   - Handle type conversions (e.g., date to ISO string)
   - Ensure nested structures are properly formatted

3. **Timestamp Management**
   - Use `firestore.SERVER_TIMESTAMP` for timestamps
   - Convert between Python `date` and ISO strings
   ```python
   # Save
   data['base_date'] = base_date.isoformat()
   
   # Load
   base_date = datetime.fromisoformat(data['base_date']).date()
   ```

4. **Backup Strategy**
   ```python
   def create_backup(self):
       backup_data = {
           'group_ids': self.load_group_ids(),
           'groups': self.load_groups(),
           'base_date': self.load_base_date(),
           'backup_time': datetime.now().isoformat()
       }
       
       doc_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
       self.db.collection('backups').document(doc_id).set(backup_data)
   ```

5. **Security Rules**
   Set appropriate Firestore security rules:
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /bot_config/{document} {
         allow read, write: if request.auth != null;
       }
       match /backups/{document} {
         allow read, write: if request.auth != null;
       }
     }
   }
   ```

### Migration Pattern

To migrate from local files to Firebase:
```python
def migrate_from_local_files(self, local_data):
    success_count = 0
    total_count = 0
    
    if 'group_ids' in local_data:
        total_count += 1
        if self.save_group_ids(local_data['group_ids']):
            success_count += 1
    
    # ... repeat for other data types
    
    return success_count == total_count
```

### Monitoring & Statistics

```python
def get_statistics(self):
    stats = {
        'firebase_available': True,
        'collections': {},
        'total_documents': 0
    }
    
    collections = ['bot_config', 'backups']
    for collection_name in collections:
        collection_ref = self.db.collection(collection_name)
        docs = list(collection_ref.stream())
        doc_count = len(docs)
        stats['collections'][collection_name] = doc_count
        stats['total_documents'] += doc_count
    
    return stats
```

### Reference Links

- [Firebase Console](https://console.firebase.google.com/)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin Python SDK](https://firebase.google.com/docs/admin/setup)
- [Railway.app Deployment](https://railway.app)
