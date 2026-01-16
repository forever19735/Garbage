---
description: Implement a new bot command with validation and help
---

# Add New Command

This workflow guides you through implementing a new command for the LINE Bot.

## Prerequisites

- Understanding of the command pattern in `main.py`
- Python development environment

## Steps

### 1. Define Command Specification

Document the command design:

**Command syntax:**
```
@commandname arg1 arg2
```

**Purpose:**
What does this command do?

**Arguments:**
- arg1: description, type, validation rules
- arg2: description, type, optional/required

**Response:**
What message should the bot send back?

**Example:**
```
@reminder 18:00
→ Sets reminder time to 18:00
```

### 2. Locate Command Handler

Open `main.py` and find the message handler:

```python
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()
    group_id = get_group_id_from_event(event)
    
    if text.startswith('@'):
        parts = text[1:].split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Commands are handled here
```

### 3. Implement Command Logic

Add new command handling:

```python
elif command == 'yourcommand':
    # Step 1: Validate arguments
    if len(args) < 1:
        reply_text = (
            "❌ 參數不足\n\n"
            "格式：@yourcommand arg1 arg2\n"
            "範例：@yourcommand value1 value2\n\n"
            "使用 @help yourcommand 查看詳細說明"
        )
    else:
        try:
            # Step 2: Parse and validate arguments
            arg1 = validate_arg1(args[0])
            arg2 = args[1] if len(args) > 1 else default_value
            
            # Step 3: Execute command logic
            result = execute_your_command(group_id, arg1, arg2)
            
            # Step 4: Format success response
            if result['success']:
                reply_text = f"✅ {result['message']}"
            else:
                reply_text = f"❌ {result['message']}"
                
        except ValueError as e:
            # Step 5: Handle validation errors
            reply_text = f"❌ 格式錯誤：{e}\n\n使用 @help yourcommand 查看說明"
        except Exception as e:
            # Step 6: Handle unexpected errors
            print(f"Command error: {e}")
            reply_text = "❌ 執行失敗，請稍後再試"
```

### 4. Create Validation Function

Add validation for command arguments:

```python
def validate_arg1(value):
    """
    Validate argument 1
    
    Args:
        value: Raw string value from user
        
    Returns:
        Validated and converted value
        
    Raises:
        ValueError: If validation fails
    """
    # Example: Validate number
    try:
        num = int(value)
        if num < 1:
            raise ValueError("必須大於 0")
        return num
    except ValueError:
        raise ValueError("必須是有效數字")
```

### 5. Implement Business Logic

Create the main function:

```python
def execute_your_command(group_id, arg1, arg2):
    """
    Execute the command logic
    
    Args:
        group_id: LINE group ID
        arg1: Validated argument 1
        arg2: Validated argument 2
        
    Returns:
        dict: {'success': bool, 'message': str}
    """
    # Validate group exists
    if group_id not in groups:
        return {
            'success': False,
            'message': '群組未註冊'
        }
    
    # Execute your logic
    # ... your implementation ...
    
    # Save to Firebase if data changed
    save_groups()
    
    return {
        'success': True,
        'message': f'已完成：{arg1}, {arg2}'
    }
```

### 6. Add Help Documentation

Update the help system in `get_help_message()`:

**Add to main help:**
```python
if topic is None:
    return """
📖 垃圾輪值提醒 Bot 使用指南

🔍 查詢指令：
  @yourcommand - 你的指令說明
  @schedule - 查看本群組推播排程
  ...
"""
```

**Add detailed help topic:**
```python
elif topic == 'yourcommand':
    return """
🆕 Your Command 指令說明

📝 基本用法：
  @yourcommand arg1 arg2
  簡短描述命令功能

💡 範例：
  @yourcommand value1 value2
  → 執行結果說明

⚠️ 注意事項：
  - 注意事項1
  - 注意事項2
"""
```

### 7. Test the Command

**Local Testing:**
```bash
# Start the bot locally
python main.py
```

**In LINE:**
1. Send command in test group:
   ```
   @yourcommand test1 test2
   ```

2. Verify response is correct

3. Test error cases:
   ```
   @yourcommand
   @yourcommand invalid
   ```

4. Check help:
   ```
   @help yourcommand
   ```

### 8. Verify Firebase Integration

Check that data persists:

1. Send command that modifies data
2. Restart Railway app
3. Verify data is still there
4. Check Firestore console for updated documents

### 9. Update Documentation

Update `README.md`:

```markdown
## 📋 指令大全

### 🆕 Your Command
- `@yourcommand arg1 arg2` - 指令說明
  - arg1: 參數說明
  - arg2: 參數說明
```

### 10. Deploy

Commit and push changes:

```bash
git add main.py README.md
git commit -m "Add @yourcommand feature"
git push origin main
```

Railway will auto-deploy.

## Checklist

- [ ] Command specification documented
- [ ] Command handler implemented
- [ ] Validation functions created
- [ ] Business logic implemented
- [ ] Help documentation added
- [ ] Local testing completed
- [ ] Error cases tested
- [ ] Firebase integration verified
- [ ] README updated
- [ ] Deployed to Railway

## Best Practices

**Validation:**
- Always validate user input
- Provide clear error messages
- Show examples in error responses

**Response Messages:**
- Use ✅ for success, ❌ for errors
- Keep messages concise
- Include emojis for visual clarity

**Error Handling:**
- Catch specific exceptions
- Log errors for debugging
- Never expose technical details to users

**Firebase:**
- Always call save functions after data changes
- Check group_id exists before operating
- Handle Firebase connection failures gracefully

**Testing:**
- Test happy path
- Test all error cases
- Test with multiple groups
- Verify data persistence

## Example: Complete Command Implementation

See existing commands in `main.py`:
- `@time` - Simple single argument
- `@week` - Multiple arguments with parsing
- `@schedule` - Query command (read-only)
- `@help` - Hierarchical help system

## Troubleshooting

**Command Not Recognized:**
- Check command name matches exactly (case-insensitive)
- Verify `elif command == 'yourcommand':` is in handler
- Redeploy if needed

**Arguments Not Parsing:**
- Debug with print statements
- Check `parts` and `args` values
- Verify split logic

**Data Not Saving:**
- Ensure `save_groups()` is called
- Check Firebase connection in logs
- Verify Firestore security rules

**Help Not Showing:**
- Check `get_help_message()` function
- Verify topic name matches command
- Test with `@help yourcommand`
