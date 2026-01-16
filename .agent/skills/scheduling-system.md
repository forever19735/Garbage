---
name: Scheduling System
description: Implement automated scheduling with APScheduler for multi-group timed broadcasts and rotation management
---

## When to use this skill

Use this skill when you need to:
- Set up automated scheduled tasks and reminders
- Implement cron-like job scheduling
- Manage per-group independent schedules
- Calculate rotation cycles based on natural weeks
- Handle timezone-aware scheduling (Asia/Taipei)
- Dynamically add/remove scheduled jobs
- Implement weekly member rotation logic

## How to use it

### Core Components

#### 1. APScheduler Setup
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Initialize scheduler
scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))
scheduler.start()
```

#### 2. Data Structures

**Group Schedule Configuration:**
```python
group_schedules = {
    "C群組ID1": {
        "days": "mon,wed,fri",  # or ["mon", "wed", "fri"]
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

**Member Rotation Structure:**
```python
groups = {
    "C群組ID1": {
        "1": ["Alice", "Bob"],
        "2": ["Charlie"],
        "3": ["David", "Eve"]
    }
}
```

#### 3. Natural Week Calculation

Calculate current week based on Monday-Sunday cycles:
```python
from datetime import date, timedelta

def get_current_week(group_id, base_date):
    """
    Calculate current week number based on natural weeks (Mon-Sun)
    
    Args:
        group_id: Group identifier
        base_date: Reference date for week 1
    
    Returns:
        int: Current week number (1-based)
    """
    today = date.today()
    
    # Get Monday of base_date's week
    base_monday = base_date - timedelta(days=base_date.weekday())
    
    # Get Monday of today's week
    today_monday = today - timedelta(days=today.weekday())
    
    # Calculate weeks difference
    weeks_diff = (today_monday - base_monday).days // 7
    
    # Calculate current week (循環)
    total_weeks = len(groups[group_id])
    current_week = (weeks_diff % total_weeks) + 1
    
    return current_week
```

#### 4. Per-Day Member Assignment

Support different members for different weekdays within same week:
```python
def get_current_day_member(group_id, target_date=None):
    """
    Get the member responsible for today based on broadcast days
    
    Args:
        group_id: Group identifier
        target_date: Target date (default: today)
    
    Returns:
        str: Member name or None if not a broadcast day
    """
    if target_date is None:
        target_date = date.today()
    
    # Get week's members
    current_members = get_current_group(group_id)
    if not current_members:
        return None
    
    # Get broadcast days for this group
    schedule = group_schedules.get(group_id, {})
    broadcast_days = schedule.get('days', '')
    
    if isinstance(broadcast_days, str):
        broadcast_days = [d.strip() for d in broadcast_days.split(',')]
    
    # Day mapping
    day_mapping = {
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    # Get today's weekday
    today_weekday = target_date.weekday()
    today_day_name = [k for k, v in day_mapping.items() if v == today_weekday][0]
    
    if today_day_name not in broadcast_days:
        return None  # Not a broadcast day
    
    # Assign member based on broadcast day index
    day_index = broadcast_days.index(today_day_name)
    member_index = day_index % len(current_members)
    
    return current_members[member_index]
```

#### 5. Dynamic Job Scheduling

**Add/Update Group Schedule:**
```python
def update_group_schedule(group_id, days_str, hour, minute):
    """
    Update or create schedule for a specific group
    
    Args:
        group_id: Group identifier
        days_str: Comma-separated days (e.g., "mon,wed,fri")
        hour: Hour (0-23)
        minute: Minute (0-59)
    """
    # Save schedule to database
    group_schedules[group_id] = {
        'days': days_str,
        'hour': hour,
        'minute': minute
    }
    save_group_schedules(group_schedules)
    
    # Remove old job if exists
    job_id = f"reminder_{group_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    # Add new job
    days = [d.strip().lower() for d in days_str.split(',')]
    trigger = CronTrigger(
        day_of_week=','.join(days),
        hour=hour,
        minute=minute,
        timezone=pytz.timezone('Asia/Taipei')
    )
    
    scheduler.add_job(
        func=send_reminder,
        trigger=trigger,
        id=job_id,
        args=[group_id],
        replace_existing=True
    )
```

**Remove Group Schedule:**
```python
def remove_group_schedule(group_id):
    """Remove scheduled job for a group"""
    job_id = f"reminder_{group_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    if group_id in group_schedules:
        del group_schedules[group_id]
        save_group_schedules(group_schedules)
```

#### 6. Reminder Function

```python
def send_reminder(group_id):
    """
    Send reminder message to a specific group
    Called by scheduler at configured times
    """
    try:
        # Get today's responsible member(s)
        member = get_current_day_member(group_id)
        
        if not member:
            print(f"No broadcast for {group_id} today")
            return
        
        # Format message
        today = date.today()
        weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        weekday = weekday_names[today.weekday()]
        
        message = f"🗑️ 今天 {today.strftime('%m/%d')} ({weekday}) 輪到 {member} 收垃圾！"
        
        # Send via LINE Messaging API
        messaging_api.push_message(
            PushMessageRequest(
                to=group_id,
                messages=[TextMessage(text=message)]
            )
        )
        
        print(f"✅ Sent reminder to {group_id}: {member}")
    except Exception as e:
        print(f"❌ Failed to send reminder to {group_id}: {e}")
```

### Best Practices

1. **Timezone Awareness**
   - Always use `Asia/Taipei` timezone for Taiwan
   - Use `pytz` for timezone handling
   - Be consistent across all datetime operations

2. **Job ID Naming**
   - Use descriptive, unique job IDs: `reminder_{group_id}`
   - Makes it easy to find and remove specific jobs

3. **Graceful Degradation**
   - Handle missing schedule configurations
   - Don't crash if a group has no members
   - Log errors but continue operation

4. **Testing Schedules**
   ```python
   # Get next run time for a job
   job = scheduler.get_job(f"reminder_{group_id}")
   if job:
       next_run = job.next_run_time
       print(f"Next reminder: {next_run}")
   ```

5. **Scheduler Lifecycle**
   ```python
   # Startup: Load all group schedules
   def init_all_schedules():
       for group_id, config in group_schedules.items():
           update_group_schedule(
               group_id,
               config['days'],
               config['hour'],
               config['minute']
           )
   
   # Shutdown: Clean up
   def shutdown():
       scheduler.shutdown(wait=True)
   ```

### Common Patterns

#### Weekly vs Daily Rotation
```python
# Weekly: Same members all week
current_members = get_current_group(group_id)

# Daily: Different member each broadcast day
today_member = get_current_day_member(group_id)
```

#### Flexible Schedule Commands
```python
# @time 18:00
# @day mon,wed,fri
# @cron mon,wed,fri 18 00

def handle_cron_command(group_id, days_str, hour, minute):
    if update_group_schedule(group_id, days_str, hour, minute):
        return f"✅ 已設定推播時間：{days_str} {hour:02d}:{minute:02d}"
    else:
        return "❌ 設定失敗"
```

### Reference Links

- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Cron Trigger Reference](https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html)
- [pytz Timezone Database](https://pythonhosted.org/pytz/)
