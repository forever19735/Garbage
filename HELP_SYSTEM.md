# 幫助系統使用指南

## 🎯 功能概述

建立了完整的 `@help` 指令系統，讓使用者可以隨時查詢所有可用的指令和使用範例。

## 🎮 幫助指令

### 基本用法

#### `@help`
顯示所有指令的總覽，包括：
- 快速查看各類別指令
- 常用指令列表
- 快速設定指令
- 基本使用提示

#### `@help 類別`
顯示特定類別的詳細指令說明：

- `@help schedule` - 排程管理指令
- `@help members` - 成員管理指令
- `@help groups` - 群組管理指令
- `@help manage` - 管理功能指令
- `@help test` - 查看和調試指令

#### `@help examples`
顯示完整的指令範例集，包括：
- 快速開始流程
- 各種情境的實用範例
- 進階使用技巧

## 📋 指令分類

### ⏰ 排程管理 (`@help schedule`)
```
@schedule - 查看目前推播排程
@settime HH:MM - 設定推播時間
@setday 星期 - 設定推播星期
@setcron 星期 時 分 - 同時設定星期和時間
```

### 👥 成員管理 (`@help members`)
```
@members - 顯示完整輪值表
@setweek 週數 成員1,成員2 - 設定整週成員
@addmember 週數 成員名 - 添加成員到指定週
@removemember 週數 成員名 - 從指定週移除成員
```

### 📱 群組管理 (`@help groups`)
```
@groups - 顯示已設定的群組列表
@info - 顯示詳細群組資訊
@debug - 自動添加當前群組 ID
```

### 🧪 查看和調試 (`@help test`)
```
@status - 完整系統狀態摘要
@schedule - 排程資訊
@members - 成員輪值表
@groups - 群組列表
@info - 詳細群組資訊
```

## 🚀 使用範例

### 新手入門流程
```
1. @help              # 查看總覽
2. @debug             # 添加群組 ID
3. @help schedule     # 學習排程設定
4. @settime 18:00     # 設定推播時間
5. @help members      # 學習成員管理
6. @setweek 1 Alice,Bob # 設定成員
7. @status            # 查看系統狀態
```

### 查詢特定功能
```
@help schedule        # 學習如何設定推播時間
@help examples        # 查看詳細範例
@help members         # 學習成員輪值管理
```

### 快速參考
```
@help                 # 最常用，快速查看所有指令
```

## 🔧 技術實現

### 函數結構

#### `get_help_message(category=None)`
- **參數**: `category` - 指定類別 ('schedule', 'members', 'groups', 'manage', 'test')
- **返回**: 格式化的幫助訊息字串
- **功能**: 根據類別返回對應的幫助內容

#### `get_command_examples()`
- **返回**: 完整的指令範例集
- **功能**: 提供實用的指令使用範例

### LINE Bot 整合

指令解析邏輯：
```python
if event.message.text.strip().startswith("@help"):
    parts = event.message.text.strip().split(maxsplit=1)
    if len(parts) == 1:
        help_text = get_help_message()           # 總覽
    elif parts[1] == "examples":
        help_text = get_command_examples()       # 範例
    else:
        category = parts[1].lower()
        if category in ["schedule", "members", "groups", "manage", "test"]:
            help_text = get_help_message(category)  # 特定類別
        else:
            help_text = "❌ 未知類別..."           # 錯誤訊息
```

## 📱 實際使用效果

### `@help` 輸出範例
```
🤖 垃圾收集提醒 Bot 指令大全

📋 快速查看：
@help schedule - 排程管理指令
@help members - 成員管理指令  
@help groups - 群組管理指令
@help manage - 管理功能指令
@help test - 查看和調試指令

🔥 常用指令：
@schedule - 查看推播排程
@members - 查看成員輪值表
@groups - 查看群組設定
@status - 查看系統狀態
@debug - 添加群組 ID

⚙️ 快速設定：
@settime 18:30 - 設定推播時間
@setday mon,thu - 設定推播星期
@setweek 1 Alice,Bob - 設定第1週成員

💡 提示：
- 所有時間都是台北時間
- 群組 ID 會自動記住
- 支援多群組推播
- 成員輪值自動循環

❓ 需要詳細說明請輸入：
@help 類別名稱
```

### `@help schedule` 輸出範例
```
⏰ 排程管理指令

🕐 查看排程：
@schedule - 顯示目前推播排程

⚙️ 設定排程：
@settime HH:MM - 設定推播時間
範例：@settime 18:30

@setday 星期 - 設定推播星期
範例：@setday mon,thu

@setcron 星期 時 分 - 同時設定星期和時間
範例：@setcron tue,fri 20 15

📋 支援的星期格式：
mon, tue, wed, thu, fri, sat, sun
```

## 🎉 優點

1. **層次化設計**: 從總覽到詳細，滿足不同需求
2. **實用範例**: 提供具體的使用範例，易於學習
3. **分類清晰**: 按功能分類，便於查找
4. **即時可用**: 在 LINE 群組中隨時查詢
5. **動態錯誤處理**: 對無效類別提供友善提示

現在使用者可以通過 `@help` 系統快速學習和掌握所有 Bot 功能！
