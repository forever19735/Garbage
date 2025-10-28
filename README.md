# 🗑️ LINE 垃圾收集提醒 Bot

智能群組輪值管理系統，支援 **每個群組獨立設定** 的 LINE Bot。自動推播提醒、彈性排程設定、多群組分別管理。

## ✨ 核心功能

### 🏢 多群組獨立管理
- **群組隔離**：每個 LINE 群組都有獨立的成員輪值表
- **獨立排程**：每個群組可設定不同的推播時間和星期
- **自動記錄**：Bot 加入群組時自動記錄，離開時自動清理
- **分別推播**：不同群組在各自設定的時間收到個別提醒

### 🔄 自然週輪值系統
- **智能計算**：基於真實週一到週日的自然週循環
- **彈性成員**：每週可設定不同數量的負責人
- **自動切換**：每個自然週自動輪替，無需手動管理
- **基準日期**：首次設定時自動記錄，可隨時重置

### ⏰ 彈性排程推播
- **群組專屬**：每個群組可設定專屬的推播時間
- **多日推播**：支援一週內多天推播（週一到週日）
- **即時預覽**：設定後立即顯示下次執行時間
- **台北時區**：全程使用 Asia/Taipei 時區

### 🎛️ 豐富管理功能
- **指令分類**：排程、成員、群組、測試等分類管理
- **狀態監控**：完整的系統狀態檢視
- **重置選項**：可選擇性重置不同資料
- **使用說明**：內建完整的幫助系統
- **簡化指令**：使用直觀的短指令（@time, @day, @week）

## 🚀 快速開始

### 1. 部署到 Railway

1. 到 [Railway](https://railway.app) 建立新專案
2. 連結你的 GitHub 專案（上傳此資料夾）
3. 在 Railway 中設定環境變數：

| 變數名稱 | 說明 | 必要性 |
|-----------|------|--------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 從 LINE Developers 取得 | ✅ 必要 |
| `LINE_CHANNEL_SECRET` | 從 LINE Developers 取得 | ✅ 必要 |
| `LINE_GROUP_ID` | 群組 ID（Bot 會自動管理） | ⚪ 可選 |

4. 部署完成後，將 Railway 提供的 URL 設定為 LINE Developers 的 Webhook URL

### 2. LINE Developers 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Messaging API Channel
3. 取得 **Channel Access Token** 和 **Channel Secret**
4. 在 Webhook settings 中設定你的 Railway URL
5. 將 Bot 加入到目標 LINE 群組

### 3. 初始設定（在 LINE 群組中）

```
@time 18:00                  # 設定本群組推播時間  
@day mon,thu                 # 設定本群組推播日期
@week 1 Alice,Bob            # 設定第1週成員
@week 2 Charlie,David        # 設定第2週成員
@schedule                    # 檢查本群組排程狀態
```

💡 **舊指令仍然支援**，新舊指令可以混用！

## �📋 指令大全

### 🔥 常用指令
- `@schedule` - 查看本群組推播排程
- `@current` - 查看本週負責人
- `@members` - 查看本群組完整輪值表  
- `@status` - 查看系統狀態

### ⚙️ 排程設定（群組專屬）
- `@time 18:30` - 設定本群組推播時間
- `@day mon,thu` - 設定本群組推播星期  
- `@cron tue,fri 20 15` - 同時設定星期和時間

### 👥 成員管理（群組專屬）
- `@week 1 Alice,Bob` - 設定第1週成員
- `@addmember 1 Charlie` - 添加成員到第1週
- `@removemember 1 Alice` - 從第1週移除成員
- `@clear_week 1` - 清空第1週成員

### 🔄 重置功能
- `@reset_date` - 重置基準日期為今天
- `@backup` - 手動創建數據備份（用於部署環境）
- `@latest_backup` - 查看最新自動備份內容

### 🤖 自動備份功能
- **數據變更自動備份**：設定成員、排程時自動備份
- **定期自動備份**：每天凌晨 02:00 自動備份
- **啟動時自動備份**：系統啟動時自動備份一次
- **備份檔案**：latest_backup.txt 儲存最新備份資料

### ❓ 幫助系統
- `@help` - 顯示完整指令列表
- `@help schedule` - 排程管理指令說明
- `@help members` - 成員管理指令說明
- `@help manage` - 管理功能指令說明

## 🎯 多群組使用情境

### 情境：辦公室多部門各自管理

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
- **pytz** - 時區處理

### 特色設計
- **群組隔離儲存**：每個群組的資料完全分離
- **獨立排程管理**：每個群組有自己的推播任務
- **自然週算法**：基於週一為起始的真實週期計算
- **容錯設計**：完整的例外處理和錯誤提示
- **模組化結構**：清晰的功能分離和程式架構

### 資料結構
```json
{
  "groups.json": {
    "C群組ID1": {
      "1": ["Alice", "Bob"],
      "2": ["Charlie"]
    },
    "C群組ID2": {
      "1": ["David", "Eve"],
      "2": ["Frank"]
    }
  },
  "group_schedules.json": {
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

# 4. 執行應用
python main.py
```

### 測試功能
```python
# 測試群組獨立功能
from main import get_current_group, update_schedule

# 查看特定群組當前負責人
current = get_current_group("C群組ID")
print(f"群組當前負責人: {current}")

# 設定群組專屬排程
result = update_schedule("C群組ID", "mon,fri", 8, 30)
print(f"排程設定結果: {result}")
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發規範
- 使用 Python 標準的程式碼風格
- 新增功能請包含適當的註解
- 重要變更請更新 README

## 💾 數據持久化

### 部署環境數據保留
為了避免在雲端平台（如 Railway、Heroku）部署更新時遺失設定，本系統提供完整的自動備份功能：

#### 🤖 自動備份功能
系統具備多層次的自動備份機制：

**1. 數據變更自動備份**
- 設定成員時自動備份（@week, @addmember, @removemember）
- 設定排程時自動備份（@time, @day, @cron）
- 確保每次重要變更都有最新備份

**2. 定期自動備份**
- 每天凌晨 02:00 自動執行完整備份
- 無需手動操作，全自動運行
- 將備份資料保存到 `latest_backup.txt`

**3. 啟動時自動備份**
- 系統啟動時自動備份當前狀態
- 為即將到來的操作提供保護

#### 📋 手動備份指令
除了自動備份，也可手動執行：

```
@backup          # 手動創建完整備份
@latest_backup   # 查看最新自動備份內容
```

#### ⚙️ 設定環境變數
將備份資料設定到部署平台：

**自動備份檔案方式：**
1. 查看 `latest_backup.txt` 檔案內容
2. 複製完整的備份字串

**手動備份指令方式：**
1. 執行 `@backup` 指令
2. 複製產生的備份資料

**設定環境變數：**
- 環境變數名稱：`GARBAGE_BOT_PERSISTENT_DATA`
- 環境變數值：備份產生的完整字串

**Railway 設定方式：**
1. 進入專案設定 → Variables
2. 新增環境變數 `GARBAGE_BOT_PERSISTENT_DATA`
3. 貼上備份資料

**Heroku 設定方式：**
```bash
heroku config:set GARBAGE_BOT_PERSISTENT_DATA="備份資料"
```

#### 🔄 自動恢復
系統啟動時會自動檢查環境變數備份：
- ✅ **有備份**：自動恢復所有設定
- ⚠️ **無備份**：使用本地檔案（可能在部署時遺失）

#### 💡 備份優勢
**自動化程度高：**
- 無需記住手動備份
- 數據變更即時保護
- 定期備份雙重保障

**便利性強：**
- 一個環境變數包含所有資料
- 備份資料自動壓縮
- 支援完整數據恢復

**可靠性佳：**
- 多層次備份機制
- 啟動時自動恢復
- 容錯設計完善

> 💡 **建議**：定期檢查 `@latest_backup` 確認備份狀態，重要變更後可手動執行 `@backup` 立即更新環境變數

### 問題回報
請在 Issue 中包含：
- 問題描述
- 復現步驟  
- 執行環境資訊
- 相關截圖或日誌

## 📜 授權條款

MIT License - 詳見 LICENSE 檔案

## 🔗 相關連結

- [LINE Developers](https://developers.line.biz/)
- [Railway 部署平台](https://railway.app)
- [Flask 官方文件](https://flask.palletsprojects.com/)
- [APScheduler 文件](https://apscheduler.readthedocs.io/)

---

⭐ 如果這個專案對你有幫助，請給個 Star！

🎯 **特色功能：真正的多群組獨立管理，每個群組都有自己的輪值表和推播時間！**