# Agent Skills

這個目錄包含了針對「垃圾輪值提醒 Bot」專案的 AI Agent 技能文件。每個技能文件定義了特定領域的開發知識和最佳實踐。

## 📚 可用技能

### 1. LINE Bot Development
**檔案**: `line-bot-development.md`

**用途**: 開發和維護 LINE 訊息 API 整合
- LINE Bot SDK v3 使用方法
- Webhook 事件處理
- 指令模式實作
- 群組訊息管理

**適用情境**:
- 實作新的 Bot 指令
- 處理 JOIN/LEAVE 事件
- 傳送推播訊息
- 除錯 Webhook 問題

---

### 2. Firebase Integration
**檔案**: `firebase-integration.md`

**用途**: 整合 Google Firebase Firestore 雲端資料庫
- Firebase 初始化設定
- CRUD 操作模式
- 資料模型設計
- 備份策略

**適用情境**:
- 設定 Firestore 資料存儲
- 實作資料持久化
- 從本地檔案遷移到雲端
- 監控 Firebase 使用狀況

---

### 3. Scheduling System
**檔案**: `scheduling-system.md`

**用途**: 使用 APScheduler 實作自動化排程系統
- 定時任務設置
- 自然週計算邏輯
- 多群組獨立排程
- Timezone 處理

**適用情境**:
- 設定定時推播提醒
- 實作週輪替邏輯
- 動態新增/移除排程
- 計算當週負責成員

---

### 4. Multi-Group Architecture
**檔案**: `multi-group-architecture.md`

**用途**: 設計支援多群組的獨立配置架構
- 群組資料隔離
- 自動註冊機制
- 情境感知操作
- 從單群組遷移

**適用情境**:
- 支援多個 LINE 群組
- 實作群組獨立設定
- 處理 JOIN/LEAVE 清理
- 設計可擴展架構

---

### 5. Command Design
**檔案**: `command-design.md`

**用途**: 設計直觀易用的 Bot 指令介面
- 指令解析模式
- 輸入驗證
- 幫助系統設計
- 錯誤處理

**適用情境**:
- 設計新的 Bot 指令
- 實作指令驗證
- 建立多層次幫助選單
- 改善使用者體驗

---

### 6. Railway Deployment
**檔案**: `deployment-railway.md`

**用途**: 部署 Python Flask 應用到 Railway.app
- 環境變數設定
- Webhook 配置
- 日誌監控
- 問題排查

**適用情境**:
- 部署 Bot 到生產環境
- 設定 LINE Webhook
- 監控應用狀態
- 解決部署問題

---

## 🎯 如何使用

### 給 AI Agent
當處理相關任務時，參考對應的技能文件：

```
問題：如何實作新的 @reminder 指令？
參考：command-design.md + line-bot-development.md

問題：Bot 加入新群組後如何自動設定？
參考：multi-group-architecture.md

問題：如何計算本週應該由誰收垃圾？
參考：scheduling-system.md
```

### 給開發者
1. 選擇相關的技能文件
2. 閱讀「When to use this skill」章節
3. 參考「How to use it」中的程式碼範例
4. 查看專案中的實際實作

## 📖 技能文件格式

每個技能文件遵循以下結構：

```markdown
---
name: 技能名稱
description: 簡短描述
---

## When to use this skill
列出適用情境

## How to use it
### 核心元件
### 最佳實踐
### 常見模式
### 參考連結
```

## 🔗 相關文件

- `README.md` - 專案主文件
- `FIREBASE_SETUP_GUIDE.md` - Firebase 設定指南
- `main.py` - 主要應用程式
- `firebase_service.py` - Firebase 服務層

## 💡 貢獻

新增技能文件時，請：
1. 遵循現有格式
2. 包含實際程式碼範例
3. 說明適用情境
4. 更新此 README

---

⭐ 這些技能文件旨在幫助 AI Agent 和開發者快速理解專案架構和最佳實踐。
