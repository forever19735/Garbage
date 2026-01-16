---
name: Multi-Group Architecture
description: Design and implement independent per-group configurations for LINE Bot supporting multiple groups simultaneously
---

## When to use this skill

Use this skill when you need to:
- Support multiple LINE groups with independent configurations
- Implement group isolation for data and settings
- Handle group join/leave events automatically
- Manage per-group member lists and schedules
- Design scalable multi-tenant bot architecture
- Migrate from single-group to multi-group system

## How to use it

### Core Principles

1. **Group Isolation**: Each group has completely separate data
2. **Automatic Registration**: Groups auto-register when bot joins
3. **Independent Scheduling**: Each group can have different broadcast times
4. **Context-Aware**: All operations require group_id context

### Data Architecture

#### 1. Group Registry
```python
# List of all registered groups
group_ids = [
    "C1234567890abcdef1234567890abcdef",
    "C9876543210fedcba9876543210fedcba"
]
```

#### 2. Per-Group Member Data
```python
groups = {
    "C群組ID1": {
        "1": ["Alice", "Bob"],
        "2": ["Charlie"],
        "3": ["David", "Eve"]
    },
    "C群組ID2": {
        "1": ["Frank"],
        "2": ["Grace", "Henry"]
    }
}
```

#### 3. Per-Group Schedules
```python
group_schedules = {
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
```

#### 4. Per-Group Custom Messages (Optional)
```python
group_messages = {
    "C群組ID1": {
        "reminder_template": "🗑️ 今天輪到 {members} 收垃圾！"
    },
    "C群組ID2": {
        "reminder_template": "📢 {members} 請記得收垃圾喔！"
    }
}
```

### Implementation Patterns

#### 1. Extracting Group ID from Event
```python
def get_group_id_from_event(event):
    """
    Extract group ID from LINE event
    
    Returns:
        str: Group ID or None if not from a group
    """
    try:
        if hasattr(event.source, 'group_id'):
            return event.source.group_id
        else:
            # Private chat, not a group
            return None
    except Exception as e:
        print(f"Failed to get group ID: {e}")
        return None
```

#### 2. Group Join Event Handler
```python
@handler.add(JoinEvent)
def handle_join(event):
    """
    Auto-register group when bot joins
    """
    group_id = get_group_id_from_event(event)
    
    if group_id and group_id not in group_ids:
        # Register new group
        group_ids.append(group_id)
        save_group_ids()
        
        # Initialize empty group data
        groups[group_id] = {}
        save_groups()
        
        # Send welcome message
        welcome_msg = (
            "👋 感謝加入垃圾輪值提醒 Bot！\n\n"
            "📝 請使用以下指令設定：\n"
            "@time 18:00 - 設定推播時間\n"
            "@day mon,wed,fri - 設定推播日期\n"
            "@week 1 小明,小華 - 設定第1週成員\n\n"
            "使用 @help 查看完整指令列表"
        )
        
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=welcome_msg)]
            )
        )
        
        print(f"✅ New group registered: {group_id}")
```

#### 3. Group Leave Event Handler
```python
@handler.add(LeaveEvent)
def handle_leave(event):
    """
    Clean up when bot leaves a group
    """
    group_id = get_group_id_from_event(event)
    
    if group_id:
        # Remove from group list
        if group_id in group_ids:
            group_ids.remove(group_id)
            save_group_ids()
        
        # Clean up group data
        if group_id in groups:
            del groups[group_id]
            save_groups()
        
        # Remove schedule
        if group_id in group_schedules:
            del group_schedules[group_id]
            save_group_schedules(group_schedules)
            
            # Remove scheduled job
            job_id = f"reminder_{group_id}"
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
        
        print(f"🗑️ Group cleaned up: {group_id}")
```

#### 4. Context-Aware Operations

**Always pass group_id to functions:**
```python
def get_current_group(group_id):
    """Get current week members for specific group"""
    if group_id not in groups:
        return []
    
    group_data = groups[group_id]
    # ... calculation logic
    return current_members

def get_member_schedule(group_id):
    """Get schedule info for specific group"""
    if group_id not in groups:
        return {
            "total_weeks": 0,
            "current_week": 1,
            "group_id": group_id,
            "current_members": []
        }
    
    # ... schedule logic
    return schedule_info
```

#### 5. Command Handler with Group Context
```python
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()
    group_id = get_group_id_from_event(event)
    
    # Require group context
    if not group_id:
        reply_text = "❌ 此 Bot 僅支援群組使用"
        messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
        return
    
    # Process commands with group context
    if text.startswith('@'):
        parts = text[1:].split()
        command = parts[0].lower()
        
        if command == 'schedule':
            # Show THIS group's schedule
            reply_text = get_schedule_info(group_id)
        elif command == 'members':
            # Show THIS group's members
            reply_text = get_member_schedule_summary(group_id)
        # ... more commands
```

### Migration Strategy

#### From Single Group to Multi-Group

**Step 1: Add Legacy Group Support**
```python
# Convert old single-group data to multi-group format
def migrate_to_multi_group():
    global groups
    
    # If groups is still a dict with week keys
    if groups and '1' in groups:
        # This is old format, migrate to new
        legacy_data = groups.copy()
        groups = {
            "legacy": legacy_data
        }
        save_groups()
        print("✅ Migrated to multi-group format")
```

**Step 2: Backward Compatible Functions**
```python
def get_current_group(group_id=None):
    """
    Support both old and new usage
    
    Args:
        group_id: Group ID (None for legacy mode)
    """
    if group_id is None:
        # Legacy mode: use first available group
        if "legacy" in groups:
            group_data = groups["legacy"]
        elif groups:
            group_data = next(iter(groups.values()))
        else:
            return []
    else:
        # New mode: use specific group
        if group_id not in groups:
            return []
        group_data = groups[group_id]
    
    # ... rest of logic
```

### Best Practices

1. **Always Validate Group ID**
   ```python
   if group_id not in groups:
       return error_response("Group not found")
   ```

2. **Consistent Storage Keys**
   Use group_id as the primary key across all dictionaries

3. **Atomic Operations**
   Update all related data together:
   ```python
   # Update members
   groups[group_id] = new_data
   save_groups()
   
   # Update schedule
   group_schedules[group_id] = new_schedule
   save_group_schedules(group_schedules)
   ```

4. **Group-Specific Responses**
   Include group context in responses when helpful:
   ```python
   reply_text = f"✅ 已更新群組設定\n\n"
   reply_text += f"📊 目前有 {len(groups[group_id])} 週輪值"
   ```

5. **Testing Multi-Group**
   - Create multiple test groups
   - Verify data isolation between groups
   - Test concurrent operations on different groups

### Firestore Schema for Multi-Group

```javascript
bot_config/
  groups/
    {
      "C群組ID1": {
        "1": ["Alice", "Bob"],
        "2": ["Charlie"]
      },
      "C群組ID2": {
        "1": ["David"],
        "2": ["Eve", "Frank"]
      }
    }
  
  group_schedules/
    {
      "C群組ID1": {
        "days": "mon,wed,fri",
        "hour": 17,
        "minute": 0
      }
    }
```

### Common Pitfalls

❌ **Don't**: Assume single group
```python
current_members = get_current_group()  # Which group?
```

✅ **Do**: Always specify group
```python
current_members = get_current_group(group_id)
```

❌ **Don't**: Share data across groups
```python
base_date = date.today()  # Global for all groups
```

✅ **Do**: Store per-group if needed
```python
group_base_dates = {
    group_id: date.today()
}
```

### Reference Patterns

See existing implementation in:
- `main.py`: Multi-group command handlers
- `firebase_service.py`: Group data storage
- `README.md`: Multi-group usage examples
