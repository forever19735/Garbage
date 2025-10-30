# 🔥 Firebase 設定完整指南

本指南將帶你完成 Firebase 的完整設定，讓你的 LINE Bot 運行在企業級的雲端資料庫上。

## 🎯 設定目標

完成後你將擁有：
- ✅ Firebase Firestore 雲端資料庫
- ✅ 服務帳戶認證金鑰
- ✅ 完整的環境變數設定
- ✅ 可立即部署的設定檔

## 📋 步驟一：建立 Firebase 專案

### 1. 前往 Firebase Console
打開瀏覽器，前往：https://console.firebase.google.com/

### 2. 建立新專案
1. 點擊「**建立專案**」
2. 輸入專案名稱（例如：`garbage-bot`）
3. 選擇是否啟用 Google Analytics（建議關閉，簡化設定）
4. 點擊「**建立專案**」

### 3. 等待專案建立完成
通常需要 1-2 分鐘，建立完成後點擊「**繼續**」

## 🗂️ 步驟二：啟用 Firestore Database

### 1. 進入 Firestore
在 Firebase 控制台左側選單中點擊「**Firestore Database**」

### 2. 建立資料庫
1. 點擊「**建立資料庫**」
2. 選擇「**以測試模式啟動**」（安全規則較寬鬆，方便開發）
3. 選擇資料庫位置：
   - 建議選擇 `asia-southeast1` (新加坡)
   - 或 `asia-east1` (台灣)
4. 點擊「**完成**」

### 3. 確認資料庫建立成功
看到 Firestore 介面表示成功建立

## 🔑 步驟三：建立服務帳戶金鑰

### 1. 前往專案設定
1. 點擊左上角的「**齒輪圖示**」
2. 選擇「**專案設定**」

### 2. 進入服務帳戶頁面
點擊「**服務帳戶**」分頁

### 3. 產生金鑰
1. 找到「**Firebase Admin SDK**」區段
2. 確認語言選擇為「**Node.js**」
3. 點擊「**產生新的私密金鑰**」
4. 在彈出視窗中點擊「**產生金鑰**」

### 4. 下載並保存 JSON 檔案
1. JSON 檔案會自動下載
2. **重要**：妥善保存此檔案，不要外洩
3. 開啟檔案，複製完整的 JSON 內容

## ⚙️ 步驟四：設定環境變數

### JSON 格式範例
你的 JSON 檔案內容會類似這樣：
```json
{
  "type": "service_account",
  "project_id": "garbage-bot-xxxxx",
  "private_key_id": "xxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIB...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@garbage-bot-xxxxx.iam.gserviceaccount.com",
  "client_id": "xxxxx",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40garbage-bot-xxxxx.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

### Railway 部署設定
1. 在 Railway 專案中點擊「**Variables**」
2. 新增以下環境變數：

| 變數名稱 | 值 |
|----------|---|
| `FIREBASE_CONFIG_JSON` | 完整的 JSON 內容（一行，不要換行） |
| `LINE_CHANNEL_ACCESS_TOKEN` | 你的 LINE Bot Token |
| `LINE_CHANNEL_SECRET` | 你的 LINE Bot Secret |

### 本地開發設定
建立 `.env` 檔案：
```bash
FIREBASE_CONFIG_JSON={"type":"service_account","project_id":"garbage-bot-xxxxx",...}
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_Token
LINE_CHANNEL_SECRET=你的LINE_Secret
```

## ✅ 步驟五：測試設定

### 1. 部署並測試
部署你的應用程式後，在 LINE 群組中輸入：
```
@firebase
```

### 2. 確認連接成功
你應該會看到類似這樣的回應：
```
🔥 Firebase 狀態報告

✅ 連接狀態: 已連接
📊 專案 ID: garbage-bot-xxxxx
🗂️ 可用集合: bot_config
📝 文件數量: 3
⚡ 回應時間: 123ms
💾 使用配額: 少量
```

## 🔒 安全性設定（進階）

### 設定 Firestore 安全規則
1. 在 Firestore 控制台點擊「**規則**」
2. 將規則修改為：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 允許 bot_config 集合的讀寫
    match /bot_config/{document} {
      allow read, write: if true;
    }
    
    // 允許 backups 集合的讀寫
    match /backups/{document} {
      allow read, write: if true;
    }
    
    // 拒絕其他所有存取
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

3. 點擊「**發布**」

## 🚨 疑難排解

### 常見錯誤及解決方案

#### 錯誤：「Permission denied」
**原因**：Firestore 安全規則過於嚴格
**解決**：確認安全規則允許讀寫操作

#### 錯誤：「Invalid JSON」
**原因**：`FIREBASE_CONFIG_JSON` 格式錯誤
**解決**：
1. 確認 JSON 格式正確
2. 確認沒有多餘的換行或空格
3. 使用線上 JSON 驗證工具檢查

#### 錯誤：「Project not found」
**原因**：專案 ID 錯誤或專案被刪除
**解決**：確認 JSON 中的 `project_id` 正確

#### 錯誤：「Service account key expired」
**原因**：服務帳戶金鑰過期
**解決**：重新產生服務帳戶金鑰

### 除錯指令
在 LINE 群組中使用這些指令來除錯：

```
@debug_env      # 檢查環境變數設定
@firebase       # 檢查 Firebase 連接狀態
```

## 💡 最佳實踐

### 1. 安全性
- ❌ 不要將 JSON 金鑰提交到版本控制
- ✅ 使用環境變數存儲敏感資訊
- ✅ 定期輪替服務帳戶金鑰

### 2. 效能優化
- ✅ 選擇離你最近的資料庫位置
- ✅ 合理設計資料結構
- ✅ 使用適當的索引

### 3. 監控
- ✅ 定期檢查 Firebase 使用量
- ✅ 設定用量警報
- ✅ 監控應用程式錯誤日誌

## 🎉 完成設定

恭喜！你現在已經：
- ✅ 建立了 Firebase 專案
- ✅ 啟用了 Firestore 資料庫
- ✅ 建立了服務帳戶金鑰
- ✅ 設定了環境變數
- ✅ 測試了連接功能

你的 LINE Bot 現在運行在企業級的 Firebase 雲端基礎設施上！

## 📞 需要協助？

如果遇到任何問題：
1. 檢查本指南的疑難排解章節
2. 確認所有步驟都正確執行
3. 在專案 Issue 中回報問題

---

🚀 **恭喜你完成 Firebase 設定！現在享受雲端的強大功能吧！**
