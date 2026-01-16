# Agent Skills

這個目錄包含了針對「垃圾輪值提醒 Bot」專案的 AI Agent 技能文件。每個技能文件定義了特定領域的開發知識和最佳實踐。

## 📚 可用技能

### 🎨 UX & 設計

#### 1. UX Command Interface Analysis
**檔案**: `ux-command-analysis.md`

**用途**: 評估和改進 Bot 指令介面的使用者體驗
- UX 成熟度評分
- 痛點識別和分析
- 快速改進建議（Quick Wins）
- 長期 UX 增強計畫

**適用情境**:
- 評估指令介面可用性
- 識別使用者工作流程中的摩擦點
- 規劃 UX 改進或重新設計
- 新手使用者引導設計

---

### 🏗️ 程式碼品質

#### Code Refactoring with SOLID Principles
**檔案**: `code-refactoring-solid.md`

**用途**: 使用 SOLID 原則重構 Python 程式碼
- SOLID 五大原則詳解
- 常見重構模式（Extract Class, Extract Method 等）
- Code Smells 識別
- 重構優先級建議

**適用情境**:
- 重構現有程式碼以提高可維護性
- 程式碼變得複雜難以修改
- 新增功能需要修改多個不相關部分
- 單元測試困難（緊耦合）
- 規劃架構改進

---

### 💻 技術實作

#### 1. LINE Bot Development
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

#### 2. Firebase Integration
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

#### 3. Scheduling System
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

#### 4. Multi-Group Architecture
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

#### 5. Command Design
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

### 🚀 部署與維運

#### Railway Deployment
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
問題：如何改善指令的使用者體驗？
參考：ux-command-analysis.md + command-design.md

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

每個技能文件遵循 Google Antigravity 標準格式：

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
- `.agent/workflows/` - Agent 工作流程

## 💡 貢獻

新增技能文件時，請：
1. 遵循 Google Antigravity 格式（包含 frontmatter）
2. 包含實際程式碼範例
3. 說明適用情境（When to use this skill）
4. 提供使用指南（How to use it）
5. 更新此 README

---

## 📊 技能分類總覽

| 類別 | 技能數量 | 主要用途 |
|-----|---------|---------|
| 🎨 UX & 設計 | 1 | 使用者體驗分析和改進 |
| 🏗️ 程式碼品質 | 1 | SOLID 原則和重構 |
| 💻 技術實作 | 5 | LINE Bot、Firebase、排程、架構、指令 |
| 🚀 部署維運 | 1 | Railway 部署和監控 |

**總計**: 8 個技能文件

---

⭐ 這些技能文件旨在幫助 AI Agent 和開發者快速理解專案架構和最佳實踐。

**最後更新**: 2026-01-16  
**位置**: `.agent/skills/` (Google Antigravity 標準位置)
