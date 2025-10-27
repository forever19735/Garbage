# 成員輪值管理功能使用指南

## 🎯 功能概述

這個功能讓你可以靈活管理垃圾收集的成員輪值安排，支援多週輪值和動態調整成員分配。

## 🔧 管理函數

### 1. `get_member_schedule()`
取得完整的成員輪值資訊

```python
from main import get_member_schedule

schedule = get_member_schedule()
print(f"總週數: {schedule['total_weeks']}")
print(f"目前第 {schedule['current_week']} 週")
print(f"本週負責: {schedule['current_members']}")

for week in schedule['weeks']:
    print(f"第 {week['week']} 週: {week['members']}")
```

### 2. `get_member_schedule_summary()`
取得格式化的輪值摘要（適合顯示給使用者）

```python
from main import get_member_schedule_summary

summary = get_member_schedule_summary()
print(summary)

# 輸出範例：
# 👥 垃圾收集成員輪值表
# 📅 總共 3 週輪值
# 📍 目前第 2 週
# 第 1 週: hsinwei💐、林志鴻、David
# 第 2 週: 徐意淳、D 👈 本週
# 第 3 週: Alice、Bob、Charlie
# 🗑️ 本週負責: 徐意淳, D
```

### 3. `update_member_schedule(week_num, members)`
更新指定週的成員安排

```python
from main import update_member_schedule

# 設定第 3 週的成員
result = update_member_schedule(3, ['Alice', 'Bob', 'Charlie'])
print(result['message'])

# 成功時輸出：第 3 週成員已更新為: Alice, Bob, Charlie
```

### 4. `add_member_to_week(week_num, member_name)`
添加成員到指定週

```python
from main import add_member_to_week

# 添加 David 到第 1 週
result = add_member_to_week(1, 'David')
print(result['message'])

# 成功時輸出：成員 David 已添加到第 1 週
```

### 5. `remove_member_from_week(week_num, member_name)`
從指定週移除成員

```python
from main import remove_member_from_week

# 從第 1 週移除 David
result = remove_member_from_week(1, 'David')
print(result['message'])

# 成功時輸出：成員 David 已從第 1 週移除
```

## 🎮 LINE Bot 指令

### `@members`
顯示完整的成員輪值表

```
@members
```

回覆範例：
```
👥 垃圾收集成員輪值表

📅 總共 3 週輪值
📍 目前第 2 週

第 1 週: hsinwei💐、林志鴻 　　　
第 2 週: 徐意淳、D 👈 本週
第 3 週: Alice、Bob、Charlie 　　　

🗑️ 本週負責: 徐意淳, D
```

### `@setweek`
設定指定週的所有成員（會覆蓋原有成員）

```
@setweek 週數 成員1,成員2,成員3
```

範例：
```
@setweek 1 Alice,Bob
@setweek 3 Charlie,David,Eve
```

### `@addmember`
添加成員到指定週

```
@addmember 週數 成員名
```

範例：
```
@addmember 1 Frank
@addmember 2 Grace
```

### `@removemember`
從指定週移除成員

```
@removemember 週數 成員名
```

範例：
```
@removemember 1 Alice
@removemember 2 Bob
```

## 📋 使用範例

### 基本設定流程

1. **查看當前安排**
   ```
   @members
   ```

2. **設定第一週成員**
   ```
   @setweek 1 Alice,Bob,Charlie
   ```

3. **設定第二週成員**
   ```
   @setweek 2 David,Eve,Frank
   ```

4. **添加新成員**
   ```
   @addmember 1 Grace
   ```

5. **確認更新結果**
   ```
   @members
   ```

### 動態調整範例

```
# 原始設定
@setweek 1 Alice,Bob
@setweek 2 Charlie,David

# 添加臨時成員
@addmember 1 Eve

# 移除請假成員
@removemember 2 Charlie

# 查看最終安排
@members
```

## 🔄 輪值邏輯

### 週數計算
系統使用 ISO 週數來決定當前是第幾週：
- 每年第一週從包含 1 月 4 日的那週開始
- 週數循環：如果有 3 週輪值，第 4 週會回到第 1 週

### 當前週判斷
```python
import datetime
week_num = datetime.date.today().isocalendar()[1]
current_week = (week_num - 1) % total_weeks + 1
```

### 成員分配
每天的垃圾收集分配會根據星期決定：
- 週一、週四：第一個成員
- 週二、週五：第二個成員
- 其他天：按順序輪流

## ⚠️ 注意事項

1. **週數編號**：從 1 開始，不是 0
2. **成員名稱**：支援中文、英文、表情符號
3. **自動擴展**：設定超過現有週數會自動擴展輪值表
4. **空成員列表**：不允許設定空的成員列表
5. **重複檢查**：添加成員時會檢查是否已存在

## 🎉 進階功能

### 批量操作
```python
# 程式碼中批量設定
from main import update_member_schedule

weeks_setup = {
    1: ['Alice', 'Bob'],
    2: ['Charlie', 'David'],
    3: ['Eve', 'Frank']
}

for week, members in weeks_setup.items():
    result = update_member_schedule(week, members)
    print(result['message'])
```

### 備份和還原
```python
# 備份當前設定
from main import get_member_schedule

backup = get_member_schedule()
print("備份完成:", backup)

# 還原設定（需要逐週恢復）
for week_info in backup['weeks']:
    update_member_schedule(week_info['week'], week_info['members'])
```

這個系統讓你可以靈活管理任意數量的週輪值和成員，適應各種不同的需求！
