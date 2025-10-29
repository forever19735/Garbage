# Railway API 自動更新設定指南

## 🎯 功能概述

Railway API 自動更新功能讓你的 LINE Bot 可以自動同步備份資料到 Railway 環境變數，避免部署更新時資料遺失。

## 🔧 設定步驟

### 1. 取得 Railway API Token

1. 登入 [Railway](https://railway.app)
2. 點擊右上角頭像 → **Account Settings**
3. 找到 **API Tokens** 區域
4. 點擊 **Create Token**
5. 複製產生的 Token

### 2. 設定環境變數

在 Railway 專案中設定以下環境變數：

#### 必要變數：
| 變數名稱 | 說明 | 範例值 |
|---------|------|--------|
| `RAILWAY_API_TOKEN` | Railway API Token | `your-api-token-here` |

#### 可選變數（會自動偵測）：
| 變數名稱 | 說明 | 何時需要 |
|---------|------|---------|
| `RAILWAY_PROJECT_ID` | 專案 ID | 多個專案時指定 |
| `RAILWAY_SERVICE_ID` | 服務 ID | 多個服務時指定 |

### 3. 驗證設定

在 LINE Bot 中發送以下指令：

```
@railway_status
```

應該看到：
```
✅ Railway API 連線正常

🔧 已配置的環境變數: X 個
📡 API Token: 已設定
🚀 自動同步: 啟用
```

## 🚀 功能特色

### 🔄 自動同步
- **觸發時機**：每次資料變更時自動執行
- **同步內容**：完整的群組設定、成員資料、排程設定
- **目標環境變數**：`GARBAGE_BOT_PERSISTENT_DATA`

### 🎛️ LINE Bot 指令

#### `@railway_status`
檢查 Railway API 連線狀態和配置

#### `@railway_sync`
手動觸發資料同步到 Railway

#### `@latest_backup`
查看最新的自動備份內容

### 📊 自動偵測功能

如果沒有設定 `RAILWAY_PROJECT_ID` 和 `RAILWAY_SERVICE_ID`，系統會：

1. **自動取得所有專案清單**
2. **使用第一個專案**
3. **使用第一個服務**
4. **顯示偵測結果**

例如：
```
✅ 自動發現專案: MyBot (abc123)
✅ 自動發現服務: web (def456)
```

## 🔍 問題排解

### ❌ Railway API 未配置

**錯誤訊息：**
```
❌ Railway API 未配置
請設定以下環境變數：
- RAILWAY_API_TOKEN (必需)
```

**解決方法：**
1. 確認已在 Railway 中設定 `RAILWAY_API_TOKEN`
2. 重新部署應用程式
3. 使用 `@railway_status` 驗證

### ⚠️ Railway API 連線異常

**錯誤訊息：**
```
⚠️ Railway API 連線異常
可能的問題：
- API Token 無效
- 專案權限不足
- 網路連線問題
```

**解決方法：**
1. **檢查 API Token**：確認 Token 正確且有效
2. **檢查權限**：確認 Token 有專案存取權限
3. **檢查網路**：確認應用程式可以連線到 Railway API

### ❌ 環境變數更新失敗

**錯誤訊息：**
```
❌ Railway 環境變數更新失敗
可能原因：
- API Token 權限不足
- 專案或服務 ID 錯誤
- 網路連線問題
```

**解決方法：**
1. **驗證權限**：確認 API Token 有修改環境變數的權限
2. **手動指定 ID**：設定 `RAILWAY_PROJECT_ID` 和 `RAILWAY_SERVICE_ID`
3. **檢查日誌**：查看詳細錯誤訊息

## 🎯 使用場景

### 1. 新專案部署
```bash
# 設定環境變數
RAILWAY_API_TOKEN=your-token-here

# 部署後在 LINE 中驗證
@railway_status
@railway_sync
```

### 2. 日常使用
- **自動備份**：每次設定變更時自動同步
- **手動同步**：使用 `@railway_sync` 強制同步
- **狀態檢查**：使用 `@railway_status` 確認連線

### 3. 故障復原
```
# 1. 檢查狀態
@railway_status

# 2. 手動同步
@railway_sync

# 3. 查看備份
@latest_backup

# 4. 驗證資料
@status
```

## 💡 最佳實踐

### ✅ 建議做法
- **定期檢查**：每週使用 `@railway_status` 檢查狀態
- **重要變更後同步**：手動執行 `@railway_sync` 確保同步
- **保留備份**：定期下載 `latest_backup.txt` 作為本地備份

### ⚠️ 注意事項
- **API Token 安全**：不要將 Token 提交到版本控制
- **權限管理**：只給必要的專案存取權限
- **備份驗證**：定期檢查環境變數是否正確更新

## 🔗 相關連結

- [Railway API 文件](https://docs.railway.app/reference/api)
- [Railway Console](https://railway.app/dashboard)
- [LINE Bot SDK 文件](https://developers.line.biz/)
