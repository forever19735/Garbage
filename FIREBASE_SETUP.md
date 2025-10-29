# Firebase 設置指南

本指南將幫助您設置 Firebase Firestore 來儲存垃圾收集 Bot 的資料。

## 🔥 為什麼使用 Firebase？

- **雲端儲存**: 資料永久保存，不會因部署而遺失
- **即時同步**: 多個實例間資料自動同步
- **免費額度**: Firebase 提供慷慨的免費使用額度
- **可擴展性**: 支援大量資料和高並發訪問
- **備份機制**: 自動備份到 Firebase 和本地檔案

## 🚀 快速設置

### 步驟 1: 創建 Firebase 專案

1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 點擊「添加專案」
3. 輸入專案名稱（例如：`garbage-bot`）
4. 可選：啟用 Google Analytics
5. 創建專案

### 步驟 2: 啟用 Firestore

1. 在左側選單中選擇「Firestore Database」
2. 點擊「創建資料庫」
3. 選擇「以測試模式開始」（開發階段）
4. 選擇資料庫位置（建議：`asia-east1` 或 `asia-southeast1`）

### 步驟 3: 獲取服務帳戶金鑰

1. 前往「專案設定」→「服務帳戶」
2. 選擇「Firebase Admin SDK」
3. 點擊「產生新的私密金鑰」
4. 下載 JSON 檔案

## 🔧 配置方式

### 方式 1: 環境變數（推薦用於部署）

將下載的 JSON 檔案內容設定為環境變數：

```bash
FIREBASE_CONFIG_JSON='{"type":"service_account","project_id":"your-project",...}'
```

#### Railway 部署設定

1. 在 Railway Dashboard 中打開您的專案
2. 前往「Variables」頁面
3. 添加新變數：
   - 名稱：`FIREBASE_CONFIG_JSON`
   - 值：完整的 JSON 檔案內容（單行，用引號包圍）

### 方式 2: 服務帳戶檔案（適用於本地開發）

將下載的 JSON 檔案重命名為 `firebase-service-account.json` 並放在專案根目錄：

```
your-project/
├── main.py
├── firebase_service.py
├── firebase-service-account.json  ← 這裡
└── requirements.txt
```

### 方式 3: Google Cloud 預設憑證

如果在 Google Cloud 環境中運行，系統會自動使用預設憑證。

## 📊 Firestore 資料結構

Bot 會在 Firestore 中創建以下結構：

```
bot_config (集合)
├── group_ids (文件)
│   ├── group_ids: ["C1234567890", "C0987654321"]
│   └── updated_at: 2024-01-15T10:30:00Z
├── groups (文件)
│   ├── groups: {
│   │   "C1234567890": {
│   │     "1": ["Alice", "Bob"],
│   │     "2": ["Charlie", "David"]
│   │   }
│   │ }
│   └── updated_at: 2024-01-15T10:30:00Z
├── base_date (文件)
│   ├── base_date: "2024-01-15"
│   └── set_at: 2024-01-15T10:30:00Z
└── group_schedules (文件)
    ├── schedules: {
    │   "C1234567890": {
    │     "days": "mon,thu",
    │     "hour": 18,
    │     "minute": 0
    │   }
    │ }
    └── updated_at: 2024-01-15T10:30:00Z

backups (集合)
├── backup_20240115_103000 (文件)
└── backup_20240115_203000 (文件)
```

## 🔐 安全性設定

### 開發階段（測試模式）

Firestore 規則：
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### 生產環境（建議）

更安全的 Firestore 規則：
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 只允許服務帳戶訪問
    match /bot_config/{document} {
      allow read, write: if request.auth != null;
    }
    match /backups/{document} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 🧪 測試 Firebase 連接

部署後，在 LINE 群組中輸入以下指令來測試：

```
@firebase
```

成功的話會顯示：
```
🔥 Firebase 狀態報告
✅ 連接狀態: 已連接
📊 資料統計: ...
```

## 📱 Bot 指令說明

### Firebase 相關指令

- `@firebase` - 檢查 Firebase 連接狀態和資料統計
- `@status` - 查看完整系統狀態（包含 Firebase）
- `@backup` - 手動創建 Firebase 備份

### 資料遷移

如果您之前使用本地檔案，Bot 會自動偵測並將資料遷移到 Firebase：

1. Bot 啟動時會檢查 Firebase 是否可用
2. 如果可用且發現本地檔案，會自動遷移
3. 遷移完成後，所有新資料都會同步到 Firebase

## 🔄 混合模式運作

Bot 採用混合模式運作：

1. **優先級**: Firebase > 本地檔案 > 環境變數備份
2. **讀取**: 優先從 Firebase 讀取，失敗時使用本地檔案
3. **寫入**: 同時寫入 Firebase 和本地檔案（雙重保障）
4. **備份**: 自動創建 Firebase 備份和環境變數備份

## 🐛 常見問題

### Q: Firebase 連接失敗怎麼辦？

A: 檢查以下項目：
1. JSON 檔案格式是否正確
2. 專案 ID 是否正確
3. 服務帳戶是否有 Firestore 權限
4. 網絡連接是否正常

### Q: 資料會不會遺失？

A: 不會，Bot 使用多重備份機制：
1. Firebase 雲端儲存
2. 本地檔案備份
3. 環境變數備份
4. 定期自動備份

### Q: Firebase 免費額度夠用嗎？

A: 對於一般使用完全足夠：
- 每日讀取：50,000 次
- 每日寫入：20,000 次
- 每日刪除：20,000 次
- 儲存空間：1 GB

### Q: 如何查看 Firebase 中的資料？

A: 在 Firebase Console 中：
1. 前往「Firestore Database」
2. 瀏覽 `bot_config` 和 `backups` 集合
3. 查看各個文件的資料

## 🆘 獲取幫助

如果遇到問題：

1. 檢查 Bot 日誌輸出
2. 使用 `@firebase` 指令檢查狀態
3. 確認 Firebase Console 中的專案設定
4. 檢查服務帳戶權限

## 🎯 最佳實踐

1. **定期備份**: 使用 `@backup` 指令定期創建備份
2. **監控用量**: 在 Firebase Console 監控 API 用量
3. **安全規則**: 生產環境請設定適當的 Firestore 規則
4. **環境分離**: 開發和生產使用不同的 Firebase 專案
