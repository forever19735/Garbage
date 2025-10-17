# LINE 群組 ID 管理函數使用指南

## 新增的函數

### 1. `get_line_group_ids()`
取得目前設定的 LINE 群組 ID 詳細資訊

```python
from main import get_line_group_ids

# 取得群組資訊
info = get_line_group_ids()
print(info)

# 輸出範例：
# {
#     'group_ids': ['C1234567890abcdef12345', 'C9876543210fedcba98765'],
#     'count': 2,
#     'is_configured': True,
#     'valid_ids': ['C1234567890abcdef12345', 'C9876543210fedcba98765']
# }
```

### 2. `add_line_group_id(group_id)`
添加新的群組 ID 到列表中

```python
from main import add_line_group_id

# 添加群組 ID
result = add_line_group_id('C1234567890abcdef12345')
print(result)

# 成功時輸出：
# {'success': True, 'message': '成功添加群組 ID: C1234567890abcdef12345', 'total_groups': 1}

# 失敗時輸出：
# {'success': False, 'message': '群組 ID C1234567890abcdef12345 已存在'}
```

### 3. `remove_line_group_id(group_id)`
從列表中移除指定的群組 ID

```python
from main import remove_line_group_id

# 移除群組 ID
result = remove_line_group_id('C1234567890abcdef12345')
print(result)

# 成功時輸出：
# {'success': True, 'message': '成功移除群組 ID: C1234567890abcdef12345', 'total_groups': 0}
```

## 新增的 LINE Bot 指令

### `@info`
顯示詳細的群組 ID 資訊，包括：
- 總群組數
- 有效/無效群組數
- 完整的群組列表

### `@groups`
顯示簡要的群組列表

### `@debug`
在群組中使用，自動添加當前群組 ID（已優化，使用新的管理函數）

## 實用範例

### 檢查群組設定狀態
```python
from main import get_line_group_ids

info = get_line_group_ids()
if info['is_configured']:
    print(f"已設定 {info['count']} 個群組")
    print(f"有效群組: {len(info['valid_ids'])} 個")
else:
    print("尚未設定任何群組")
```

### 批量添加群組 ID
```python
from main import add_line_group_id

group_ids_to_add = [
    'C1234567890abcdef12345',
    'C9876543210fedcba98765',
    'Cabcdef1234567890abcd'
]

for gid in group_ids_to_add:
    result = add_line_group_id(gid)
    if result['success']:
        print(f"✅ 成功添加: {gid}")
    else:
        print(f"❌ 添加失敗: {result['message']}")
```

### 清理無效的群組 ID
```python
from main import get_line_group_ids, remove_line_group_id

info = get_line_group_ids()
invalid_ids = [gid for gid in info['group_ids'] if gid not in info['valid_ids']]

for gid in invalid_ids:
    result = remove_line_group_id(gid)
    print(f"移除無效群組 ID: {gid}")
```

## 注意事項

1. **群組 ID 格式**：必須以 'C' 開頭且長度大於 10 個字符
2. **重複檢查**：函數會自動檢查重複的群組 ID
3. **安全性**：`get_line_group_ids()` 返回副本，避免外部修改原始資料
4. **持久性**：群組 ID 只在程式運行期間保存，重啟後需重新設定
