# 🗑️ LINE 垃圾輪值提醒 Bot

智能群組輪值管理系統，支援 **每個群組獨立設定** 的 LINE Bot。自動推播提醒、彈性排程設定、多群組分別管理。

✨ **Firebase 純雲端架構 - 企業級可靠性，無需複雜設定**

## ✨ 核心功能

### 🏢 多群組獨立管理
- **群組隔離**：每個 LINE 群組都有獨立的成員輪值表
- **獨立排程**：每個群組可設定不同的推播時間和星期
- **自動記錄**：Bot 加入群組時自動記錄，離開時自動清理
- **分別推播**：不同群組在各自設定的時間收到個別提醒

### 🔄 自然週輪值系統
- **智能計算**：基於真實週一到週日的自然週循環
- **彈性成員**：每週可設定不同數量的負責人
- ### 💡 疑難排解

#### 常見問題
**Q: Firebase 連接失敗？**
A: 檢查 `FIREBASE_CONFIG_JSON` 格式是否正確，確保 JSON 完整無誤

**Q: 權限被拒絕？**
A: 確認 Firestore 安全規則允許讀寫操作

**Q: 資料未同步？**
A: 檢查網路連接，Firebase 需要穩定的網路環境播日分配不同成員
- **自動切換**：每個自然週自動輪替，無需手動管理
- **基準日期**：首次設定時自動記錄，可隨時重置

### ⏰ 彈性排程推播
- **群組專屬**：每個群組可設定專屬的推播時間
- **多日推播**：支援一週內多天推播（週一到週日）
- **即時預覽**：設定後立即顯示下次執行時間
- **台北時區**：全程使用 Asia/Taipei 時區

### 🎛️ 簡化使用體驗
- **直觀指令**：使用簡單的短指令（@time, @day, @week）
- **自動化管理**：群組自動記錄，無需手動設定
- **即時反饋**：指令執行後立即顯示結果
- **內建幫助**：完整的使用說明系統

### 🚀 快速開始

### 1. Firebase 設定（一次性設定）

1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 **Firestore Database**
4. 在專案設定中建立 **服務帳戶金鑰**
5. 下載 JSON 憑證檔案，複製完整內容

### 2. 部署到 Railway

1. 到 [Railway](https://railway.app) 建立新專案
2. 連結你的 GitHub 專案（上傳此資料夾）  
3. 在 Railway 中設定環境變數：

| 變數名稱 | 說明 | 必要性 |
|-----------|------|--------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 從 LINE Developers 取得 | ✅ 必要 |
| `LINE_CHANNEL_SECRET` | 從 LINE Developers 取得 | ✅ 必要 |
| `FIREBASE_CONFIG_JSON` | Firebase 服務帳戶完整 JSON | ✅ 必要 |

💡 **只需要 3 個環境變數，設定超簡單！**

4. 部署完成後，將 Railway 提供的 URL 設定為 LINE Developers 的 Webhook URL

### 3. LINE Developers 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Messaging API Channel
3. 取得 **Channel Access Token** 和 **Channel Secret**
4. 在 Webhook settings 中設定你的 Railway URL
5. 將 Bot 加入到目標 LINE 群組

### 4. 初始設定（在 LINE 群組中）

```
@time 18:00                  # 設定本群組推播時間  
@day mon,thu                 # 設定本群組推播日期
@week 1 Alice,Bob            # 設定第1週成員
@week 2 Charlie,David        # 設定第2週成員
@schedule                    # 檢查本群組排程狀態
```

## 📋 指令大全

### 🔥 常用指令
- `@schedule` - 查看本群組推播排程
- `@members` - 查看本群組完整輪值表

### ⚙️ 排程設定（群組專屬）
- `@time 18:30` - 設定本群組推播時間
- `@day mon,thu` - 設定本群組推播星期  
- `@cron tue,fri 20 15` - 同時設定星期和時間

### 👥 成員管理（群組專屬）
- `@week 1 Alice,Bob` - 設定第1週成員
- `@addmember 1 Charlie` - 添加成員到第1週
- `@removemember 1 Alice` - 從第1週移除成員

### ❓ 幫助系統
- `@help` - 顯示完整指令列表
- `@help schedule` - 排程管理指令說明
- `@help members` - 成員管理指令說明
- `@help groups` - 群組管理指令說明

## 🎯 使用情境範例

### 情境 1：週內按日輪值
```
@week 1 Debby,John           # 第1週：Debby, John
@day mon,thu                 # 星期一和星期四推播
@time 09:00                  # 每天 09:00 提醒
```
**實際運作效果：**
- **星期一 09:00**：推播 "輪到 Debby 收垃圾！"
- **星期四 09:00**：推播 "輪到 John 收垃圾！"
- **週內不同日期有不同負責人**

### 情境 2：多部門獨立管理

**部門 A 群組設定：**
```
@time 17:00                  # A部門：每天 17:00 提醒
@day mon,wed,fri             # 週一、三、五提醒
@week 1 張小明,李小華         # 第1週：張小明、李小華
@week 2 王大雄               # 第2週：王大雄
```

**部門 B 群組設定：**
```
@time 09:00                  # B部門：每天 09:00 提醒
@day tue,thu                 # 週二、四提醒
@week 1 陳小美               # 第1週：陳小美
@week 2 林志明,黃大同         # 第2週：林志明、黃大同
```

**實際運作效果：**
- 部門 A：週一三五 17:00 收到自己的成員提醒
- 部門 B：週二四 09:00 收到自己的成員提醒
- 完全獨立運作，互不干擾

## 🛠️ 技術架構

### 核心技術棧
- **Flask** - Web 框架
- **LINE Bot SDK v3** - LINE 訊息處理
- **APScheduler** - 背景排程任務（支援多群組排程）
- **Firebase Firestore** - 雲端資料庫存儲
- **pytz** - 時區處理

### 特色設計
- **Firebase 純雲端**：所有資料存儲在 Google Firebase
- **群組隔離儲存**：每個群組的資料完全分離
- **獨立排程管理**：每個群組有自己的推播任務
- **自然週算法**：基於週一為起始的真實週期計算
- **容錯設計**：完整的例外處理和錯誤提示
- **模組化結構**：清晰的功能分離和程式架構

### 雲端架構優勢
- **無單點故障**：Firebase 分散式架構
- **自動擴展**：隨使用量自動調整
- **全球同步**：多地區資料中心
- **即時備份**：自動版本控制和恢復
- **零維護**：無需管理資料庫或伺服器

### 資料結構
```json
{
  "Firebase Firestore 集合": {
    "bot_config/groups": {
      "C群組ID1": {
        "1": ["Alice", "Bob"],
        "2": ["Charlie"]
      },
      "C群組ID2": {
        "1": ["David", "Eve"],
        "2": ["Frank"]
      }
    },
    "bot_config/group_schedules": {
      "C群組ID1": {
        "days": "mon,wed,fri",
        "hour": 17,
        "minute": 0
      },
      "C群組ID2": {
        "days": "tue,thu",
        "hour": 9,
        "minute": 30
      }
    },
    "backups/": {
      "[timestamp]": "自動備份記錄"
    }
  }
}
```

## 📊 推播訊息範例

**群組 A 收到的訊息：**
```
🗑️ 今天 10/28 (週二) 輪到 Alice、Bob 收垃圾！
```

**群組 B 收到的訊息：**
```
🗑️ 今天 10/28 (週二) 輪到 David 收垃圾！
```

## 🔧 本地開發

### 環境需求
- Python 3.8+
- pip

### 安裝步驟
```bash
# 1. 克隆專案
git clone https://github.com/forever19735/Garbage.git
cd Garbage

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數（建立 .env 檔案）
echo "LINE_CHANNEL_ACCESS_TOKEN=你的_access_token" > .env
echo "LINE_CHANNEL_SECRET=你的_channel_secret" >> .env
echo "FIREBASE_CONFIG_JSON=你的_firebase_config_json" >> .env

# 4. 執行應用
python main.py
```

### 測試功能
```python
# 測試 Firebase 連接
from firebase_service import firebase_service_instance

# 檢查 Firebase 狀態
status = firebase_service_instance.is_available()
print(f"Firebase 連接狀態: {status}")

# 測試成員輪值功能
from main import get_current_group

# 查看特定群組當前負責人
current = get_current_group("C群組ID")
print(f"群組當前負責人: {current}")
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發規範
- 使用 Python 標準的程式碼風格
- 新增功能請包含適當的註解
- 重要變更請更新 README

## ☁️ Firebase 雲端存儲

### 🔥 Firebase 優勢
本系統採用 Google Firebase Firestore 作為雲端資料庫，提供：

#### 🚀 企業級可靠性
- **99.99% 可用性**：Google 全球基礎設施
- **自動備份**：即時版本控制和災難恢復
- **多地區同步**：全球資料中心分散式存儲
- **零單點故障**：分散式架構設計

#### ⚡ 開發者友善
- **即時同步**：資料變更立即生效
- **無需維護**：Google 負責所有基礎設施
- **自動擴展**：隨使用量自動調整效能
- **簡單設定**：只需一個 JSON 憑證檔案

#### 🔒 安全性保障
- **加密傳輸**：HTTPS/TLS 加密
- **存取控制**：Firebase 安全規則
- **身分驗證**：服務帳戶金鑰驗證
- **審計日誌**：完整的操作記錄

### 📋 Firebase 設定步驟

#### 1. 建立 Firebase 專案
1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 點擊「建立專案」或選擇現有專案
3. 按照指示完成專案設定

#### 2. 啟用 Firestore Database
1. 在 Firebase 控制台選擇「Firestore Database」
2. 點擊「建立資料庫」
3. 選擇「測試模式」（之後可調整安全規則）
4. 選擇資料庫位置（建議選擇亞洲地區）

#### 3. 建立服務帳戶
1. 前往「專案設定」→「服務帳戶」
2. 點擊「產生新的私密金鑰」
3. 下載 JSON 檔案
4. 複製 JSON 檔案的完整內容

#### 4. 設定環境變數
將 JSON 內容設定為 `FIREBASE_CONFIG_JSON` 環境變數：

**Railway 設定：**
```
FIREBASE_CONFIG_JSON={"type": "service_account", "project_id": "your-project", ...}
```

**本地開發 (.env)：**
```
FIREBASE_CONFIG_JSON={"type": "service_account", "project_id": "your-project", ...}
```

### 🔍 Firebase 監控

#### 檢查連接狀態
```
@help                   # 查看可用指令  
```

### 💡 Firebase 最佳實踐

#### 資料結構設計
- **集合隔離**：不同類型資料存在不同集合
- **文件 ID 規範**：使用有意義的 ID 命名
- **巢狀資料**：合理使用子集合和巢狀物件

#### 安全規則建議
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /bot_config/{document} {
      allow read, write: if true; // 開發階段，生產環境應加強限制
    }
    match /backups/{document} {
      allow read, write: if true;
    }
  }
}
```

#### 效能優化
- **批次操作**：使用 batch 寫入減少請求次數
- **索引建立**：為查詢欄位建立適當索引
- **快取策略**：適當使用本地快取減少讀取

### � 疑難排解

#### 常見問題
**Q: Firebase 連接失敗？**
A: 檢查 `FIREBASE_CONFIG_JSON` 格式是否正確，確保 JSON 完整無誤

**Q: 權限被拒絕？**
A: 確認 Firestore 安全規則允許讀寫操作

**Q: 資料未同步？**
A: 檢查網路連接，Firebase 需要穩定的網路環境

#### 除錯工具
```
@debug_env          # 檢查環境變數設定
@firebase           # 查看 Firebase 狀態和統計
```

### 問題回報
請在 Issue 中包含：
- 問題描述
- 復現步驟  
- 執行環境資訊
- 相關截圖或日誌

## 📜 授權條款

MIT License - 詳見 LICENSE 檔案

## 🔗 相關文件

- 📚 `FIREBASE_SETUP_GUIDE.md` - **Firebase 完整設定指南**（推薦新手）
- 🔧 `FIREBASE_SETUP.md` - Firebase 詳細設定說明
- 🏗️ `AI_輔助案例_多群組LINE_Bot架構重構.md` - 架構重構案例
- 📊 `儲存策略分析.md` - 資料儲存策略分析

## 🌐 外部連結

- [LINE Developers](https://developers.line.biz/)
- [Railway 部署平台](https://railway.app)
- [Firebase Console](https://console.firebase.google.com/)
- [Flask 官方文件](https://flask.palletsprojects.com/)
- [APScheduler 文件](https://apscheduler.readthedocs.io/)

---

⭐ 如果這個專案對你有幫助，請給個 Star！

🎯 **核心功能：簡潔易用的多群組輪值管理 + Firebase 企業級雲端存儲！**