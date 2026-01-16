# 🗑️ Garbage Duty Bot

LINE 群組輪值管理機器人，支援多群組獨立排程與 Firebase 雲端存儲。

## ✨ 核心特色

- **多群組管理**：各群組獨立設定輪值表與推播時間，互不干擾。
- **自然週循環**：自動按週次輪替成員，每週可設定不同負責人。
- **彈性排程**：支援自由指定星期與時間推播 (e.g., 每週一、四 18:00)。
- **雲端存儲**：整合 Firebase Firestore，資料安全可靠，無需擔心資料遺失。

## 📋 指令列表

| 類別 | 指令 | 說明 |
| :--- | :--- | :--- |
| **排程設定** | `@time 18:30` | 設定本群組推播時間 |
| | `@day mon,thu` | 設定本群組推播星期 (週一, 週四) |
| | `@cron tue 20 15` | 進階設定：週二 20:15 推播 |
| | `@schedule` | 查看本群組目前的排程設定 |
| **輪值管理** | `@week 1 Alice` | 設定第 1 週負責人為 Alice |
| | `@week 2 Bob,Cat` | 設定第 2 週負責人為 Bob 和 Cat |
| | `@members` | 查看本群組完整輪值表 |
| **系統** | `@help` | 顯示完整指令說明 |

## 🚀 快速開始

詳細設定步驟請參閱以下文件：
- **Firebase 設定**：請見 [FIREBASE_SETUP_GUIDE.md](FIREBASE_SETUP_GUIDE.md)
- **測試與開發**：請見 [TESTING_GUIDE.md](TESTING_GUIDE.md)

### 部署所需的環境變數

| 變數名稱 | 說明 |
| :--- | :--- |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API Channel Access Token |
| `LINE_CHANNEL_SECRET` | LINE Messaging API Channel Secret |
| `FIREBASE_CONFIG_JSON` | Firebase Service Account 的完整 JSON 字串 |

## 🛠️ 技術架構

- **Web Framework**: Flask
- **Bot Interface**: LINE Messaging API SDK v3
- **Scheduling**: APScheduler (BackgroundScheduler)
- **Database**: Firebase Firestore
- **Timezone**: pytz (Asia/Taipei)

---
[MIT License](LICENSE)