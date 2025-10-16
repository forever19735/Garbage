# 🗑️ LINE 垃圾收取提醒 Bot

自動每週一、四提醒誰要收垃圾。

## 🚀 部署步驟

1. 到 [Railway](https://railway.app) 建立新專案
2. 連結你的 GitHub 專案（上傳此資料夾）
3. 在 Railway 中設定以下環境變數：

| 變數名稱 | 說明 |
|-----------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | 從 LINE Developers 取得 |
| `LINE_CHANNEL_SECRET` | 從 LINE Developers 取得 |
| `LINE_GROUP_ID` | 群組 ID（Bot 加入群組後再補上） |

4. 部署完成後，將 URL 設定成 LINE Developers 的 Webhook  

