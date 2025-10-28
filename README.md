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
@settime 18:00               # 設定本群組推播時間  
@setday mon,thu              # 設定本群組推播日期
@week 1 Alice,Bob            # 設定第1週成員
@week 2 Charlie,David        # 設定第2週成員
@schedule                    # 檢查本群組排程狀態
```

## 📋 指令大全

### 🔥 常用指令
- `@schedule` - 查看本群組推播排程
- `@current` - 查看本週負責人
- `@members` - 查看本群組完整輪值表  
- `@status` - 查看系統狀態

### ⚙️ 排程設定（群組專屬）
- `@settime 18:30` - 設定本群組推播時間
- `@setday mon,thu` - 設定本群組推播星期  
- `@setcron tue,fri 20 15` - 同時設定星期和時間

### 👥 成員管理（群組專屬）
- `@week 1 Alice,Bob` - 設定第1週成員
- `@addmember 1 Charlie` - 添加成員到第1週
- `@removemember 1 Alice` - 從第1週移除成員
- `@clear_week 1` - 清空第1週成員

###  重置功能
- `@reset_date` - 重置基準日期為今天

### ❓ 幫助系統
- `@help` - 顯示完整指令列表
- `@help schedule` - 排程管理指令說明
- `@help members` - 成員管理指令說明
- `@help manage` - 管理功能指令說明

## 🎯 多群組使用情境

### 情境：辦公室多部門各自管理

**部門 A 群組設定：**
```
@settime 17:00               # A部門：每天 17:00 提醒
@setday mon,wed,fri          # 週一、三、五提醒
@week 1 張小明,李小華         # 第1週：張小明、李小華
@week 2 王大雄               # 第2週：王大雄
```

**部門 B 群組設定：**
```
@settime 09:00               # B部門：每天 09:00 提醒
@setday tue,thu              # 週二、四提醒
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

## 🎉 版本亮點

### v2.0 - 多群組獨立管理
- ✅ 每個群組獨立的成員輪值表
- ✅ 每個群組獨立的推播時間設定
- ✅ 群組專屬的指令處理
- ✅ 自動群組管理（加入/離開）
- ✅ 完全向後相容

### 主要改進
- **架構升級**：從單一全域管理升級到多群組隔離管理
- **使用者體驗**：每個群組只看到自己的設定，不會被其他群組影響
- **管理便利性**：不同群組可以有完全不同的輪值安排和時間
- **擴充性**：支援無限數量的群組同時使用

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

🎯 **特色功能：真正的多群組獨立管理，每個群組都有自己的輪值表和推播時間！**