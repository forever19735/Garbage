# 🗑️ LINE 垃圾收集提醒 Bot

智能成員輪值管理系統，支援自然週計算的 LINE Bot。自動推播提醒、彈性排程設定、多群組管理。

## ✨ 核心功能

### 🔄 自然週輪值系統
- **智能計算**：基於真實週一到週日的自然週循環
- **彈性成員**：每週可設定不同數量的負責人
- **自動切換**：每個自然週自動輪替，無需手動管理
- **基準日期**：首次設定時自動記錄，可隨時重置

### ⏰ 彈性排程推播
- **自訂時間**：任意設定推播時間（24小時制）
- **多日推播**：支援一週內多天推播（週一到週日）
- **即時預覽**：設定後立即顯示下次執行時間
- **台北時區**：全程使用 Asia/Taipei 時區

### 📱 多群組管理
- **自動偵測**：Bot 加入群組後自動記錄群組 ID
- **多群同步**：支援同時推播到多個 LINE 群組
- **持久儲存**：群組設定永久保存，重啟後不遺失

### 🎛️ 豐富管理功能
- **指令分類**：排程、成員、群組、測試等分類管理
- **狀態監控**：完整的系統狀態檢視
- **重置選項**：可選擇性重置不同資料
- **使用說明**：內建完整的幫助系統

## 🚀 快速開始

### 1. 部署到 Railway

1. 到 [Railway](https://railway.app) 建立新專案
2. 連結你的 GitHub 專案（上傳此資料夾）
3. 在 Railway 中設定環境變數：

| 變數名稱 | 說明 | 必要性 |
|-----------|------|--------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 從 LINE Developers 取得 | ✅ 必要 |
| `LINE_CHANNEL_SECRET` | 從 LINE Developers 取得 | ✅ 必要 |
| `LINE_GROUP_ID` | 群組 ID（可透過 `@debug` 指令自動取得） | ⚪ 可選 |

4. 部署完成後，將 Railway 提供的 URL 設定為 LINE Developers 的 Webhook URL

### 2. LINE Developers 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Messaging API Channel
3. 取得 **Channel Access Token** 和 **Channel Secret**
4. 在 Webhook settings 中設定你的 Railway URL
5. 將 Bot 加入到目標 LINE 群組

### 3. 初始設定（在 LINE 群組中）

```
@debug                        # 添加群組 ID
@settime 18:00               # 設定推播時間  
@setday mon,thu              # 設定推播日期
@setweek 1 Alice,Bob         # 設定第1週成員
@setweek 2 Charlie,David     # 設定第2週成員
@status                      # 檢查設定狀態
```

## 📋 指令大全

### 🔥 常用指令
- `@schedule` - 查看推播排程
- `@members` - 查看成員輪值表  
- `@groups` - 查看群組設定
- `@status` - 查看系統狀態
- `@debug` - 添加群組 ID

### ⚙️ 排程設定
- `@settime 18:30` - 設定推播時間
- `@setday mon,thu` - 設定推播星期  
- `@setcron tue,fri 20 15` - 同時設定星期和時間

### 👥 成員管理
- `@setweek 1 Alice,Bob` - 設定第1週成員
- `@addmember 1 Charlie` - 添加成員到第1週
- `@removemember 1 Alice` - 從第1週移除成員
- `@clear_week 1` - 清空第1週成員
- `@clear_members` - 清空所有成員

### 📱 群組管理
- `@info` - 顯示詳細群組資訊
- `@clear_groups` - 清空所有群組 ID

### 🔄 重置功能
- `@reset_date` - 重置基準日期為今天
- `@reset_all` - 重置所有資料（謹慎使用）

### ❓ 幫助系統
- `@help` - 顯示完整指令列表
- `@help schedule` - 排程管理指令說明
- `@help members` - 成員管理指令說明
- `@help groups` - 群組管理指令說明

## 🛠️ 技術架構

### 核心技術棧
- **Flask** - Web 框架
- **LINE Bot SDK v3** - LINE 訊息處理
- **APScheduler** - 背景排程任務
- **pytz** - 時區處理

### 特色設計
- **持久化儲存**：使用 JSON 檔案儲存所有設定
- **自然週算法**：基於週一為起始的真實週期計算
- **容錯設計**：完整的例外處理和錯誤提示
- **模組化結構**：清晰的功能分離和程式架構

## 📊 使用範例

### 情境：公司垃圾收集輪值

**設定過程：**
```
# 1. 添加群組並設定排程
@debug                        # 記錄群組 ID
@settime 17:00               # 每天 17:00 提醒
@setday mon,wed,fri          # 週一、三、五提醒

# 2. 設定輪值成員（3週循環）
@setweek 1 張小明,李小華      # 第1週：張小明、李小華
@setweek 2 王大雄            # 第2週：王大雄
@setweek 3 陳小美,林志明,黃大同 # 第3週：陳小美、林志明、黃大同

# 3. 檢查設定
@status                      # 檢視完整狀態
@members                     # 檢視輪值表
```

**推播訊息範例：**
```
🗑️ 垃圾收集提醒

📅 日期：2025年10月27日 (週一)
👥 本週負責人：張小明、李小華

請記得收集垃圾！🙏
```

## 🔧 本地開發

### 環境需求
- Python 3.8+
- pip

### 安裝步驟
```bash
# 1. 克隆專案
git clone https://github.com/你的用戶名/垃圾收集提醒Bot.git
cd 垃圾收集提醒Bot

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
# 測試成員輪值功能
from main import get_current_group, get_member_schedule

# 查看當前負責人
current = get_current_group()
print(f"當前負責人: {current}")

# 查看完整排程
schedule = get_member_schedule()
print(f"總週數: {schedule['total_weeks']}")
print(f"當前第 {schedule['current_week']} 週")
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發規範
- 使用 Python 標準的程式碼風格
- 新增功能請包含適當的註解
- 重要變更請更新 README

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