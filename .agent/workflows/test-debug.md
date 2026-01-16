---
description: Testing and debugging procedures for LINE Bot
---

# Test and Debug

This workflow provides testing and debugging procedures for the LINE Bot.

## Quick Health Check

### 1. Check Railway Status

// turbo
```bash
# Visit your Railway URL
curl https://your-app.up.railway.app/
```

Expected: `🗑️ LINE Bot is running!`

### 2. Check Railway Logs

1. Railway dashboard → Deployments → View Logs
2. Look for:
   ```
   ✅ Firebase 可用
   ACCESS_TOKEN: [set]
   GROUP_ID: [...]
   Running on http://0.0.0.0:5000
   ```

### 3. Test in LINE

Send in test group:
```
@help
```

Bot should respond with help menu.

## Comprehensive Testing

### Test Command Functionality

**Query Commands:**
```
@schedule    # Should show schedule or "尚未設定"
@members     # Should show members or "尚未設定"
@help        # Should show main help
@help schedule  # Should show detailed help
```

**Configuration Commands:**
```
@time 18:00          # Set time
@day mon,wed,fri     # Set days
@cron tue,thu 20 15  # Set both
@schedule            # Verify settings saved
```

**Member Management:**
```
@week 1 Alice,Bob       # Set week 1
@week 2 Charlie         # Set week 2
@members                # Verify members
@addmember 1 David      # Add to week 1
@removemember 1 Alice   # Remove from week 1
@members                # Verify changes
```

### Test Error Handling

**Invalid Arguments:**
```
@time             # Missing argument
@time 25:00      # Invalid hour
@time abc        # Invalid format
@week            # Missing arguments
@week x Alice    # Invalid week number
@day xyz         # Invalid day name
```

Each should return helpful error message.

### Test Multi-Group Isolation

**Setup:**
1. Add bot to Group A
2. Add bot to Group B

**In Group A:**
```
@time 18:00
@week 1 Alice
@schedule
```

**In Group B:**
```
@time 09:00
@week 1 Bob
@schedule
```

**Verify:**
- Group A shows 18:00, Alice
- Group B shows 09:00, Bob
- Settings are independent

### Test Firebase Persistence

1. Set configuration in LINE:
   ```
   @time 18:00
   @week 1 Alice,Bob
   ```

2. Restart Railway app (or wait for redeploy)

3. Check data persisted:
   ```
   @schedule
   @members
   ```

4. Verify Firestore console shows correct data

### Test Scheduled Broadcasts

**Note**: Railway free tier apps sleep after inactivity.

**Setup:**
1. Set near-future time:
   ```
   @cron mon,tue,wed,thu,fri [current_hour] [current_minute+2]
   @week 1 TestUser
   ```

2. Wait for broadcast time

3. Check group receives message:
   ```
   🗑️ 今天 MM/DD (週X) 輪到 TestUser 收垃圾！
   ```

**Important**: For reliable testing of scheduled tasks, upgrade to Railway Hobby plan.

## Common Issues and Solutions

### Issue: Bot Not Responding

**Symptoms:**
- Bot added to group
- No response to `@help`

**Debug Steps:**
1. Check Railway logs for errors
2. Verify webhook URL in LINE Console
3. Test webhook: LINE Console → Messaging API → Verify
4. Check `LINE_CHANNEL_SECRET` matches

**Solution:**
```bash
# Verify environment variables in Railway
LINE_CHANNEL_ACCESS_TOKEN=[set]
LINE_CHANNEL_SECRET=[set]
```

### Issue: Firebase Connection Failed

**Symptoms:**
- Logs show "Firebase 未連接"
- Data not persisting

**Debug Steps:**
1. Check Railway logs for Firebase errors
2. Verify `FIREBASE_CONFIG_JSON` is set
3. Check JSON format (should be valid JSON)
4. Verify Firebase project is active

**Solution:**
- Re-download service account JSON
- Update `FIREBASE_CONFIG_JSON` in Railway
- Redeploy

### Issue: Scheduled Tasks Not Running

**Symptoms:**
- No automatic reminders at set time

**Common Causes:**
1. Railway free tier sleeps after inactivity
2. Invalid cron configuration
3. No members set for current week

**Debug:**
Check scheduler status in logs:
```
APScheduler running jobs: [job list]
Next run time: [datetime]
```

**Solution:**
- Upgrade to Railway Hobby plan ($5/mo)
- Or ping app regularly to keep awake
- Verify cron settings with `@schedule`

### Issue: Wrong Member Notified

**Symptoms:**
- Broadcast sends wrong person's name

**Debug:**
1. Check current week calculation:
   ```
   @members  # Shows current week
   ```

2. Verify base_date in Firestore

3. Check member rotation logic

**Solution:**
- Verify week numbers are correct
- Check base_date is set properly
- Test week calculation manually

### Issue: Webhook Returns 400

**Symptoms:**
- LINE webhook verification fails
- Logs show signature errors

**Debug:**
1. Verify `LINE_CHANNEL_SECRET` exact match
2. Check webhook handler signature validation
3. Review request headers in logs

**Solution:**
```python
# In main.py, verify handler uses correct secret
handler = WebhookHandler(LINE_CHANNEL_SECRET)
```

## Debugging Tools

### Enable Debug Logging

Add to `main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Redeploy and check detailed logs.

### Add Debug Endpoint

**Temporary debug route** (remove in production):
```python
@app.route("/debug/env", methods=['GET'])
def debug_env():
    return {
        "firebase_available": firebase_service_instance.is_available(),
        "groups_count": len(group_ids),
        "schedules_count": len(group_schedules)
    }
```

Visit: `https://your-app.up.railway.app/debug/env`

### Firebase Console

Check data directly:
1. Go to Firestore console
2. Navigate to `bot_config` collection
3. View documents:
   - `group_ids`
   - `groups`
   - `group_schedules`

### LINE Console Logs

Check message delivery:
1. LINE Developers Console
2. Messaging API → Statistics
3. View message counts and errors

## Manual Testing Checklist

- [ ] Bot responds to `@help`
- [ ] Can set time with `@time`
- [ ] Can set days with `@day`
- [ ] Can set members with `@week`
- [ ] `@schedule` shows correct info
- [ ] `@members` shows correct rotation
- [ ] Error messages are helpful
- [ ] Data persists after restart
- [ ] Multi-group isolation works
- [ ] Scheduled broadcasts work (if on paid plan)

## Performance Testing

### Load Test (Optional)

Send multiple commands rapidly:
```python
# Test script
commands = [
    "@schedule",
    "@members",
    "@help",
]

for cmd in commands:
    # Send command
    # Verify response
```

### Monitor Railway Metrics

Railway dashboard → Metrics:
- CPU usage
- Memory usage
- Response time

## Security Testing

**Check sensitive data:**
- Secrets not in Git
- Environment variables properly set
- Firestore rules appropriate for env
- Service account JSON secure

**Test unauthorized access:**
- Try accessing `/callback` externally
- Verify signature validation works

## After Testing

1. Remove debug endpoints
2. Disable debug logging (if enabled)
3. Review and tighten Firestore rules for production
4. Document any issues discovered
5. Update README if needed

## Continuous Monitoring

**Set up alerts:**
- Railway: Enable deploy notifications
- LINE: Monitor API quota usage
- Firebase: Set usage alerts

**Regular checks:**
- Weekly: Review Railway logs
- Monthly: Check Firebase usage
- Monitor: LINE message quotas
