# Agent Workflows

這個目錄包含了「垃圾輪值提醒 Bot」專案的實用工作流程文件。每個workflow定義了完成特定任務的詳細步驟。

## 📚 可用的 Workflows

### 🚀 /deploy
**檔案**: `deploy.md`  
**描述**: Deploy LINE Bot to Railway.app with Firebase

完整的部署流程，涵蓋：
- Railway 專案設定
- 環境變數配置
- LINE Webhook 連接
- 部署驗證

**何時使用**: 首次部署或重新部署應用程式到 Railway 平台

---

### 📱 /setup-line-bot
**檔案**: `setup-line-bot.md`  
**描述**: Configure LINE Developers Console for Messaging API

LINE Bot 完整設定流程：
- 建立 Messaging API Channel
- 配置 Webhook
- 取得憑證 (Access Token, Channel Secret)
- 測試 Bot 功能

**何時使用**: 建立新的 LINE Bot 或重新配置現有 Bot

---

### 🔥 /setup-firebase
**檔案**: `setup-firebase.md`  
**描述**: Initialize Firebase Firestore for cloud data storage

Firebase 雲端資料庫設定：
- 建立 Firebase 專案
- 啟用 Firestore
- 設定安全規則
- 取得服務帳戶憑證

**何時使用**: 首次設定 Firebase 或切換到新的 Firebase 專案

---

### ➕ /add-command
**檔案**: `add-command.md`  
**描述**: Implement a new bot command with validation and help

實作新 Bot 指令的完整指南：
- 指令規格設計
- 參數驗證
- 錯誤處理
- 幫助文件整合
- 測試流程

**何時使用**: 需要為 Bot 新增新功能或指令時

---

### 🧪 /test-debug
**檔案**: `test-debug.md`  
**描述**: Testing and debugging procedures for LINE Bot

測試與除錯指南：
- 健康檢查步驟
- 功能測試清單
- 常見問題排查
- 除錯工具使用

**何時使用**: 驗證功能、排查問題或進行日常維護

---

## 🎯 如何使用

### 在對話中使用

直接輸入 workflow 指令：
```
/deploy
/setup-line-bot
/setup-firebase
/add-command
/test-debug
```

AI Agent 會讀取對應的 workflow 並引導你完成步驟。

### 手動閱讀

直接開啟 `.agent/workflows/` 目錄下的 markdown 檔案，按照步驟執行。

## 📖 Workflow 格式說明

每個 workflow 檔案包含：

```yaml
---
description: 簡短描述
---

# Workflow 標題

## Prerequisites
前置條件

## Steps
### 1. 步驟一
詳細說明...

### 2. 步驟二
詳細說明...

## Verification
驗證清單

## Troubleshooting
常見問題解決
```

## 🔧 Workflow 特殊標記

### `// turbo`
標記在步驟上方表示該步驟可以自動執行（如果是命令）：
```markdown
// turbo
1. Run this command
```

### `// turbo-all`
標記在文件任何位置表示所有命令步驟都可自動執行。

## 🚦 建議的執行順序

### 首次設置
1. `/setup-firebase` - 設定資料庫
2. `/setup-line-bot` - 設定 LINE Bot
3. `/deploy` - 部署到 Railway
4. `/test-debug` - 驗證一切正常運作

### 日常開發
1. `/add-command` - 新增功能
2. `/test-debug` - 測試新功能
3. 提交程式碼（Railway 自動部署）

### 問題排查
1. `/test-debug` - 診斷問題
2. 查看對應 workflow 的 Troubleshooting 章節

## 🔗 相關資源

- [專案 README](../README.md) - 專案總覽
- [Firebase 設定指南](../FIREBASE_SETUP_GUIDE.md) - 詳細 Firebase 說明
- [Railway 文件](https://docs.railway.app/) - Railway 平台文件
- [LINE Developers](https://developers.line.biz/) - LINE Bot 官方文件

## 💡 貢獻

新增 workflow 時，請遵循：
1. 使用 YAML frontmatter 格式
2. 包含完整的步驟說明
3. 提供驗證清單
4. 加入常見問題排解
5. 更新此 README

---

⭐ 這些 workflows 旨在簡化開發和部署流程，提高效率！
