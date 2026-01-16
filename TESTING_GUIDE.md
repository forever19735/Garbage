# 🧪 Test & Debug Guide for LINE Bot

## 目前專案狀態檢查

### ✅ 已確認項目
- Python 3.9.6 已安裝
- Procfile 配置正確
- requirements.txt 包含所需依賴

### 📋 測試環境準備

由於這是一個需要 LINE Bot 和 Firebase 連接的應用，測試分為兩個階段：

## 階段一：本地測試（無需部署）

### 1. 檢查程式碼結構

**檢查清單：**
- [x] `main.py` - Flask 應用主程式
- [x] `firebase_service.py` - Firebase 服務層
- [x] `requirements.txt` - 依賴清單
- [x] `Procfile` - Railway 啟動配置

### 2. 驗證指令處理邏輯

可以在本地測試的部分：

**週期計算邏輯：**
```python
# 在 Python console 測試
from main import get_current_group, get_member_schedule
from datetime import date

# 測試週期計算
schedule = get_member_schedule("test_group_id")
print(f"Current week: {schedule['current_week']}")
```

**參數驗證：**
檢查 `main.py` 中的驗證函數是否正確處理錯誤輸入。

### 3. 靜態程式碼檢查

**檢查項目：**
- [ ] 環境變數使用 `os.getenv()` 
- [ ] Firebase 連接有錯誤處理
- [ ] 所有 LINE API 呼叫有 try-except
- [ ] 排程任務有群組 ID 驗證

## 階段二：部署後測試（需要 Zeabur + LINE）

### 前置條件

需要以下設定完成：
1. ✅ Zeabur 專案已部署
2. ✅ LINE Bot 已設定
3. ✅ Firebase 已配置
4. ✅ Webhook 已連接

### 快速健康檢查

**1. 檢查 Zeabur 狀態**
```bash
# 替換成您的 Zeabur URL
curl https://your-app.zeabur.app/
```
預期回應：`🗑️ LINE Bot is running!`

**2. 檢查 Zeabur 日誌**
尋找以下訊息：
```
✅ Firebase 可用
ACCESS_TOKEN: [已設定]
Running on http://0.0.0.0:5000
```

**3. 在 LINE 測試**
在測試群組發送：
```
@help
```
Bot 應該回覆幫助選單。

### 功能測試清單

#### 查詢指令
- [ ] `@schedule` - 顯示排程或「尚未設定」
- [ ] `@members` - 顯示成員或「尚未設定」
- [ ] `@help` - 顯示主幫助選單
- [ ] `@help schedule` - 顯示詳細說明

#### 配置指令
- [ ] `@time 18:00` - 設定時間
- [ ] `@day mon,wed,fri` - 設定星期
- [ ] `@cron tue,thu 20 15` - 同時設定
- [ ] `@schedule` - 驗證設定已保存

#### 成員管理
- [ ] `@week 1 Alice,Bob` - 設定第1週
- [ ] `@week 2 Charlie` - 設定第2週
- [ ] `@members` - 查看成員表
- [ ] `@addmember 1 David` - 新增成員
- [ ] `@removemember 1 Alice` - 移除成員

#### 錯誤處理
- [ ] `@time` - 缺少參數（應顯示錯誤）
- [ ] `@time 25:00` - 無效小時（應顯示錯誤）
- [ ] `@week x Alice` - 無效週數（應顯示錯誤）
- [ ] `@day xyz` - 無效星期（應顯示錯誤）

### 多群組隔離測試

**如果有兩個測試群組：**

在群組 A：
```
@time 18:00
@week 1 Alice
@schedule
```

在群組 B：
```
@time 09:00
@week 1 Bob
@schedule
```

驗證：群組 A 顯示 18:00, Alice；群組 B 顯示 09:00, Bob

### Firebase 持久化測試

1. 設定資料：
   ```
   @time 18:00
   @week 1 Alice,Bob
   ```

2. 重啟 Zeabur 應用

3. 驗證資料仍存在：
   ```
   @schedule
   @members
   ```

4. 檢查 Firestore Console 顯示正確資料

## 常見問題排查

### Bot 無回應

**症狀：** Bot 已加入群組但不回應 `@help`

**排查步驟：**
1. 檢查 Zeabur 日誌是否有錯誤
2. 驗證 LINE Console webhook URL
3. 測試 webhook：LINE Console → Verify
4. 確認 `LINE_CHANNEL_SECRET` 正確

### Firebase 連接失敗

**症狀：** 日誌顯示「Firebase 未連接」

**排查步驟：**
1. 檢查 `FIREBASE_CONFIG_JSON` 環境變數
2. 驗證 JSON 格式正確
3. 確認 Firebase 專案處於活動狀態

### 排程任務未執行

**症狀：** 沒有在設定時間收到提醒

**可能原因：**
1. Cron 配置錯誤
2. 當週沒有設定成員
3. APScheduler 未正確啟動

**解決方法：**
- 檢查 Zeabur 日誌中的 scheduler 訊息
- 使用 `@schedule` 驗證設定

## 除錯工具

### 1. 啟用除錯日誌

在 `main.py` 頂部加入：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 新增除錯端點（測試用）

```python
@app.route("/debug/env", methods=['GET'])
def debug_env():
    return {
        "firebase_available": firebase_service_instance.is_available(),
        "groups_count": len(group_ids),
        "schedules_count": len(group_schedules)
    }
```

訪問：`https://your-app.zeabur.app/debug/env`

### 3. 檢查 Firestore Console

直接查看資料：
1. 前往 Firestore console
2. 進入 `bot_config` 集合
3. 查看文件：`group_ids`, `groups`, `group_schedules`

## 下一步

### 如果尚未部署：
1. 運行 `/setup-firebase` 設定 Firebase
2. 運行 `/setup-line-bot` 設定 LINE Bot
3. 運行 `/deploy` 部署到 Zeabur
4. 再次運行此測試流程

### 如果已部署：
1. 執行上述功能測試清單
2. 記錄任何發現的問題
3. 使用除錯工具排查

### 建議的測試順序：
1. 基本健康檢查
2. 查詢指令測試
3. 配置指令測試
4. 成員管理測試
5. 錯誤處理測試
6. Firebase 持久化測試

---

**## ⚠️ 重要提醒

**Zeabur 優勢：**
- 免費版不會休眠
- 排程任務可靠運行
- 適合生產環境使用

**安全注意事項：**
- 不要將憑證提交到 Git
- 使用環境變數儲存所有敏感資訊
- 定期檢查 Firestore 安全規則

---

**下一步：** 完成部署並進行整合測試
```
