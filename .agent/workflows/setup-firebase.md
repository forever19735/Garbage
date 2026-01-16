---
description: Initialize Firebase Firestore for cloud data storage
---

# Setup Firebase

This workflow guides you through setting up Firebase Firestore for the LINE Bot project.

## Prerequisites

- Google account
- Access to Firebase Console

## Steps

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" (or "Create a project")
3. Enter project name: e.g., "garbage-duty-bot"
4. Accept Firebase terms
5. (Optional) Enable Google Analytics
6. Click "Create project"
7. Wait for project creation

### 2. Enable Firestore Database

1. In Firebase Console, select your project
2. Click "Firestore Database" in left sidebar
3. Click "Create database"
4. Choose starting mode:
   - **Test mode** (for development): Allow all read/write
   - **Production mode** (for production): Deny all by default
   - Recommendation: Start with test mode
5. Select Firestore location:
   - Choose `asia-east1` (Taiwan) or `asia-northeast1` (Tokyo)
   - **Important**: Cannot be changed later
6. Click "Enable"

### 3. Configure Security Rules

Once database is created:

1. Go to "Rules" tab
2. Update rules for development:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /bot_config/{document} {
      allow read, write: if true;
    }
    match /backups/{document} {
      allow read, write: if true;
    }
  }
}
```

3. Click "Publish"

**For Production**, use stricter rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /bot_config/{document} {
      allow read, write: if request.auth != null;
    }
    match /backups/{document} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

### 4. Create Service Account

1. Go to "Project Settings" (gear icon)
2. Select "Service accounts" tab
3. Click "Generate new private key"
4. Confirm by clicking "Generate key"
5. JSON file will download automatically
6. **Keep this file secure and private**

### 5. Prepare Firebase Credentials for Railway

1. Open the downloaded JSON file
2. Copy the ENTIRE content (it should be one long JSON object)
3. In Railway dashboard:
   - Go to Variables tab
   - Add new variable: `FIREBASE_CONFIG_JSON`
   - Paste the complete JSON
   - Click "Add"

Example format (DO NOT use this, use your own):
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

### 6. Initialize Data Structure (Optional)

You can manually create initial collections:

1. In Firestore console, click "Start collection"
2. Collection ID: `bot_config`
3. Add documents:

**Document: `group_ids`**
```json
{
  "group_ids": [],
  "updated_at": [current timestamp]
}
```

**Document: `groups`**
```json
{
  "groups": {},
  "updated_at": [current timestamp]
}
```

**Document: `group_schedules`**
```json
{
  "schedules": {},
  "updated_at": [current timestamp]
}
```

**Note**: The bot will auto-create these if they don't exist.

### 7. Verify Firebase Connection

After deploying to Railway:

// turbo
Check Railway logs for:
```
✅ Firebase 可用，直接從 Firebase 載入資料
```

Test in LINE group:
```
@help
```

Bot should respond, and you should see data in Firestore console.

### 8. Monitor Usage

1. Go to "Usage" tab in Firestore
2. Monitor:
   - Reads/writes per day
   - Storage usage
   - Network egress

**Free Tier Limits:**
- 50K reads/day
- 20K writes/day
- 1 GB storage
- 10 GB/month network egress

For most LINE groups, this is more than sufficient.

## Verification Checklist

- [ ] Firebase project created
- [ ] Firestore database enabled in Asia region
- [ ] Security rules configured
- [ ] Service account JSON downloaded
- [ ] `FIREBASE_CONFIG_JSON` added to Railway
- [ ] Railway logs show "Firebase 可用"
- [ ] Bot can store data (test with `@week 1 Alice`)

## Best Practices

**Security:**
- Never commit service account JSON to Git
- Use environment variables only
- Review security rules regularly
- Enable audit logs for production

**Data Structure:**
```
bot_config/
  ├── group_ids - List of registered groups
  ├── groups - Member rotation data per group
  ├── base_date - Week 1 starting date
  └── group_schedules - Broadcast schedule per group

backups/
  └── backup_YYYYMMDD_HHMMSS - Automatic backups
```

**Backup:**
- Firestore automatically backs up data
- Implement manual backup via bot command if needed
- Export data periodically for disaster recovery

## Next Steps

- Run `/deploy` to deploy application to Railway
- Run `/setup-line-bot` to configure LINE integration
- Run `/test-debug` to verify Firebase operations

## Troubleshooting

**"Firebase 未連接" in logs:**
- Verify `FIREBASE_CONFIG_JSON` is set in Railway
- Check JSON format is valid
- Ensure service account has Firestore permissions

**Permission Denied:**
- Check Firestore security rules
- Verify service account has "Cloud Datastore User" role
- For test mode, rules should allow all read/write

**Data Not Persisting:**
- Check Firestore console for write errors
- Verify network connectivity
- Check Railway logs for Firebase errors
- Ensure bot calls `save_groups()` after changes

**Quota Exceeded:**
- Check usage in Firestore console
- Optimize read/write operations
- Consider upgrading to Blaze plan (pay-as-you-go)
